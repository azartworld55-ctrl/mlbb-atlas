import fs from "node:fs/promises";

const BASES = ["https://arena.fastapicloud.dev/api", "https://arena.rone.dev/api"];
const read = async (path) => JSON.parse(await fs.readFile(path, "utf8"));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function records(payload) {
  const list = payload?.data?.records ?? payload?.data?.items ?? payload?.records ?? payload?.items;
  if (!Array.isArray(list)) return [];
  return list.map((entry) => entry?.data && typeof entry.data === "object" ? entry.data : entry);
}
function firstHeroRecord(payload) {
  return records(payload)[0] ?? null;
}
async function get(path) {
  let lastError;
  for (const base of BASES) {
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const response = await fetch(base + path, {
          headers: { accept: "application/json", "user-agent": "MLBB-Atlas-localization/1.0" },
          signal: AbortSignal.timeout(20000)
        });
        if (!response.ok) throw new Error(`${base}${path}: HTTP ${response.status}`);
        const json = await response.json();
        if (json?.code !== undefined && json.code !== 0) throw new Error(`${base}${path}: API code ${json.code} ${json.message || ""}`);
        return json;
      } catch (error) {
        lastError = error;
        if (attempt === 0) await sleep(500 * (attempt + 1));
      }
    }
  }
  throw lastError ?? new Error("No localization API host available");
}
async function safe(path) {
  try { return await get(path); }
  catch (error) { console.warn("Localization source unavailable:", String(error)); return null; }
}
function heroData(record) {
  return record?.hero?.data ?? record?.data?.hero?.data ?? record?.data ?? record;
}
function flattenHeroSkills(data) {
  return (data?.heroskilllist ?? []).flatMap((group) => group?.skilllist ?? []);
}
const staticSpells = {
  Execute: "Казнь", Retribution: "Возмездие", Inspire: "Вдохновение", Sprint: "Спринт",
  Revitalize: "Восстановление", Aegis: "Эгида", Petrify: "Окаменение", Purify: "Очищение",
  Flameshot: "Огненный выстрел", Flicker: "Вспышка", Arrival: "Прибытие", Vengeance: "Месть"
};
const staticEmblems = {
  Common: "Общая", All: "Общая", Tank: "Танк", Assassin: "Убийца", Mage: "Маг",
  Fighter: "Боец", Support: "Поддержка", Marksman: "Стрелок"
};
const empty = {
  generated_at: new Date().toISOString(),
  source: "Переводы ещё не загружены.",
  coverage: { heroes: 0, hero_skills: 0, items: 0, spells: 0, emblems: 0 },
  heroes: {}, items: {}, spells: {}, emblems: {}, skill_names: {}
};

async function main() {
  const [heroes, items, spells, emblems] = await Promise.all([
    read("data/heroes/current.json"), read("data/items/current.json"),
    read("data/spells/current.json"), read("data/emblems/current.json")
  ]);
  const result = structuredClone(empty);

  // Localized hero catalog gives a single, ID-stable name map for all heroes.
  const heroCatalog = await safe("/heroes?size=200&lang=ru");
  for (const row of records(heroCatalog)) {
    const key = String(row.hero_id ?? "");
    const hero = heroes.find((entry) => String(entry.id) === key);
    const name = row.hero?.data?.name;
    if (hero && name) result.heroes[hero.slug || hero.id] = { name, skills: {} };
  }

  // One detail request per hero supplies localized ability names and descriptions.
  // Keep concurrency low to avoid rate limiting on the community mirror.
  let cursor = 0;
  const worker = async () => {
    while (cursor < heroes.length) {
      const hero = heroes[cursor++];
      const payload = await safe(`/heroes/${encodeURIComponent(hero.id)}?lang=ru&size=100`);
      const row = firstHeroRecord(payload);
      if (row) {
        const data = heroData(row);
        const entry = result.heroes[hero.slug || hero.id] ?? { skills: {} };
        if (data?.name) entry.name = data.name;
        const localizedSkills = flattenHeroSkills(data);
        (hero.skills ?? []).forEach((skill, index) => {
          const translated = localizedSkills[index];
          if (!translated?.skillname) return;
          entry.skills[skill.name] = {
            name: translated.skillname,
            description: translated.skilldesc || ""
          };
          result.skill_names[hero.slug || hero.id] ??= {};
          result.skill_names[hero.slug || hero.id][skill.name] = translated.skillname;
        });
        result.heroes[hero.slug || hero.id] = entry;
      }
      await sleep(180);
    }
  };
  await Promise.all(Array.from({ length: 2 }, worker));

  const [spellRu, spellEn, itemRu, itemEn, roleRu] = await Promise.all([
    safe("/academy/spells?size=200&lang=ru"),
    safe("/academy/spells?size=200&lang=en"),
    safe("/academy/equipment/expanded?size=200&lang=ru"),
    safe("/academy/equipment/expanded?size=200&lang=en"),
    safe("/academy/roles?size=200&lang=ru")
  ]);

  if (spellRu && spellEn) {
    const ruById = new Map(records(spellRu).map((x) => [String(x.battleskillid ?? x.__data?.skillid), x]));
    for (const en of records(spellEn)) {
      const ru = ruById.get(String(en.battleskillid ?? en.__data?.skillid));
      const enName = en.__data?.skillname ?? en.skillname;
      const ruName = ru?.__data?.skillname ?? ru?.skillname;
      const ruDescription = ru?.__data?.skilldesc ?? ru?.skilldesc ?? ru?.skillshortdesc;
      if (enName && ruName) result.spells[enName] = { name: ruName, summary: ruDescription || "" };
    }
  }
  for (const spell of spells) {
    const fallback = staticSpells[spell.name];
    if (fallback) result.spells[spell.name] ??= { name: fallback, summary: spell.summary || "" };
  }

  if (itemRu && itemEn) {
    const ruById = new Map(records(itemRu).map((x) => [String(x.equipid), x]));
    for (const en of records(itemEn)) {
      const ru = ruById.get(String(en.equipid));
      if (!en?.equipname || !ru?.equipname) continue;
      result.items[en.equipname] = {
        name: ru.equipname,
        summary: ru.equiptips || "",
        description: ru.equipskilldesc || "",
        passive_names: [ru.equipskill1, ru.equipskill2, ru.equipskill3, ru.equipskill4, ru.equipskill5, ru.equipskill6, ru.equipskill7].filter(Boolean)
      };
    }
  }

  // Main emblem names are stable; localize from the game's role/emblem catalog where possible.
  for (const row of records(roleRu)) {
    const enName = row.emblem_title ?? row.emblem_detail?.data?.emblemname;
    const ruName = row.caption ?? row.emblem_detail?.data?.emblemname;
    if (enName && ruName) result.emblems[enName] = ruName;
  }
  for (const emblem of emblems) {
    const fallback = staticEmblems[emblem.name];
    if (fallback) result.emblems[emblem.name] ??= fallback;
  }

  result.coverage = {
    heroes: Object.values(result.heroes).filter((x) => x.name).length,
    hero_skills: Object.values(result.heroes).reduce((sum, x) => sum + Object.keys(x.skills || {}).length, 0),
    items: Object.keys(result.items).length,
    spells: Object.keys(result.spells).length,
    emblems: Object.keys(result.emblems).length
  };
  result.generated_at = new Date().toISOString();
  result.source = "Rone Arena API v1.6.2, lang=ru; API is community-maintained and relays publicly available MLBB game data. Static spell/emblem fallbacks are marked in source code.";
  await fs.mkdir("site/data", { recursive: true });
  await fs.writeFile("site/data/ru-localization.json", JSON.stringify(result, null, 2) + "\n");
  console.log("Russian localization coverage:", JSON.stringify(result.coverage));
  console.log(`Source records: ${heroes.length} heroes, ${items.length} items, ${spells.length} spells, ${emblems.length} emblems.`);
  if (result.coverage.heroes === 0 && result.coverage.items === 0) {
    throw new Error("Localization coverage is zero for both heroes and items; refusing to publish an empty translation file.");
  }
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
