import fs from "node:fs/promises";

const API = "https://arena.rone.dev/api";
const read = async (path) => JSON.parse(await fs.readFile(path, "utf8"));
const list = (value) => {
  const v = value?.data?.items ?? value?.data?.records ?? value?.items ?? value?.records ?? value?.data ?? value;
  return Array.isArray(v) ? v : v && typeof v === "object" ? [v] : [];
};
const one = (value) => list(value)[0] ?? value;
const get = async (path) => {
  const response = await fetch(API + path, { headers: { accept: "application/json" }, signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.json();
};
const flatSkills = (detail) => {
  const data = detail?.hero?.data ?? detail?.data?.hero?.data ?? detail?.data ?? detail;
  return (data?.heroskilllist ?? []).flatMap((group) => group?.skilllist ?? []);
};
const staticSpells = {
  Execute: "Казнь", Retribution: "Возмездие", Inspire: "Вдохновение", Sprint: "Спринт",
  Revitalize: "Восстановление", Aegis: "Эгида", Petrify: "Окаменение", Purify: "Очищение",
  Flameshot: "Огненный выстрел", Flicker: "Вспышка", Arrival: "Прибытие", Vengeance: "Месть"
};
const staticEmblems = {
  Common: "Общая", Tank: "Танк", Assassin: "Убийца", Mage: "Маг",
  Fighter: "Боец", Support: "Поддержка", Marksman: "Стрелок"
};
const empty = { generated_at: new Date().toISOString(), source: "Локальные русские подписи; сетевые переводы не получены.", heroes: {}, items: {}, spells: {}, emblems: staticEmblems, skill_names: {} };

async function safe(path) {
  try { return await get(path); } catch (error) { console.warn("Localization source unavailable:", String(error)); return null; }
}
async function main() {
  const [heroes, items, spells, emblems] = await Promise.all([
    read("data/heroes/current.json"), read("data/items/current.json"),
    read("data/spells/current.json"), read("data/emblems/current.json")
  ]);
  const result = structuredClone(empty);

  // Official game content API mirror supports lang=ru. Failures are non-fatal:
  // the site still builds and uses its bundled Russian interface.
  const [spellRu, spellEn, itemRu, itemEn] = await Promise.all([
    safe("/academy/spells?size=200&lang=ru"), safe("/academy/spells?size=200&lang=en"),
    safe("/academy/equipment/expanded?size=200&lang=ru"), safe("/academy/equipment/expanded?size=200&lang=en")
  ]);
  if (spellRu && spellEn) {
    const ruById = new Map(list(spellRu).map(x => [String(x.battleskillid), x]));
    for (const en of list(spellEn)) {
      const ru = ruById.get(String(en.battleskillid));
      const enName = en?.__data?.skillname ?? en?.skillname;
      const ruName = ru?.__data?.skillname ?? ru?.skillname;
      const ruDesc = ru?.__data?.skilldesc ?? ru?.skillshortdesc;
      if (enName && ruName) result.spells[enName] = { name: ruName, summary: ruDesc || "" };
    }
  }
  for (const spell of spells) {
    const fallback = staticSpells[spell.name];
    if (fallback) result.spells[spell.name] ??= { name: fallback, summary: spell.summary || "" };
  }

  if (itemRu && itemEn) {
    const ruById = new Map(list(itemRu).map(x => [String(x.equipid), x]));
    for (const en of list(itemEn)) {
      const ru = ruById.get(String(en.equipid));
      if (!en?.equipname || !ru?.equipname) continue;
      result.items[en.equipname] = {
        name: ru.equipname,
        summary: ru.equiptips || ru.equipskilldesc || "",
        passive_names: [ru.equipskill1, ru.equipskill2, ru.equipskill3, ru.equipskill4, ru.equipskill5, ru.equipskill6, ru.equipskill7].filter(Boolean)
      };
    }
  }

  // Hero detail endpoints provide localized skill names and descriptions.
  let cursor = 0;
  const workers = Array.from({ length: 6 }, async () => {
    while (cursor < heroes.length) {
      const hero = heroes[cursor++];
      const detail = await safe(`/heroes/${encodeURIComponent(hero.id)}?lang=ru&size=100`);
      if (!detail) continue;
      const payload = one(detail);
      const heroData = payload?.hero?.data ?? payload?.data?.hero?.data ?? payload?.data ?? payload;
      const localizedName = heroData?.name;
      const localizedSkills = flatSkills(payload);
      const entry = {};
      if (localizedName) entry.name = localizedName;
      entry.skills = {};
      (hero.skills ?? []).forEach((skill, index) => {
        const translated = localizedSkills[index];
        if (translated?.skillname) {
          entry.skills[skill.name] = { name: translated.skillname, description: translated.skilldesc || "" };
          result.skill_names[hero.slug || hero.id] ??= {};
          result.skill_names[hero.slug || hero.id][skill.name] = translated.skillname;
        }
      });
      result.heroes[hero.slug || hero.id] = entry;
    }
  });
  await Promise.all(workers);

  for (const emblem of emblems) {
    const fallback = staticEmblems[emblem.name];
    if (fallback) result.emblems[emblem.name] = fallback;
  }
  result.source = "Русская локализация игрового API (arena.rone.dev, lang=ru); резервные названия — локальный словарь.";
  await fs.mkdir("site/data", { recursive: true });
  await fs.writeFile("site/data/ru-localization.json", JSON.stringify(result, null, 2) + "\n");
  const translatedHeroes = Object.values(result.heroes).filter(x => x.name).length;
  console.log(`Russian localization prepared: ${translatedHeroes} hero names, ${Object.keys(result.items).length} item names, ${Object.keys(result.spells).length} spell names.`);
}
main().catch(async (error) => {
  console.error(error);
  await fs.mkdir("site/data", { recursive: true });
  await fs.writeFile("site/data/ru-localization.json", JSON.stringify(empty, null, 2) + "\n");
});
