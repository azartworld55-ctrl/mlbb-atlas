async function loadAtlas() {
  try {
    const [meta, heroes, items] = await Promise.all([
      fetch('/api/v1/meta').then(r => r.json()),
      fetch('/api/v1/heroes').then(r => r.json()),
      fetch('/api/v1/items').then(r => r.json())
    ]);
    document.querySelector('#hero-count').textContent = meta.collections.heroes;
    document.querySelector('#item-count').textContent = meta.collections.items;

    const list = document.querySelector('#hero-list');
    const render = rows => {
      list.replaceChildren();
      if (!rows.length) {
        list.textContent = 'Dataset is being assembled. No unverified values are shown.';
        return;
      }
      rows.forEach(hero => {
        const card = document.createElement('article');
        const title = document.createElement('strong');
        title.textContent = hero.name;
        const detail = document.createElement('p');
        detail.textContent = (hero.roles || []).join(' · ') || 'Role not recorded';
        card.append(title, detail);
        list.append(card);
      });
    };

    render(heroes.data);
    setupSkillVersions(heroes.data);
    document.querySelector('#hero-search').addEventListener('input', async event => {
      const query = event.target.value;
      const result = await fetch('/api/v1/heroes' + (query ? '?search=' + encodeURIComponent(query) : '')).then(r => r.json());
      render(result.data);
    });
    document.querySelector('#item-status').textContent = items.count
      ? items.count + ' sourced items available.'
      : 'Item records will appear after source review.';
  } catch (error) {
    document.querySelector('#hero-list').textContent = 'Could not load API. Start the backend and refresh.';
    console.error(error);
  }
}

function setupCalculator() {
  const form = document.querySelector('#formula-form');
  const result = document.querySelector('#formula-result');
  if (!form || !result) return;

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const base = Number(document.querySelector('#formula-base').value);
    const attack = Number(document.querySelector('#formula-attack').value);
    const coefficient = Number(document.querySelector('#formula-coefficient').value);
    if (![base, attack, coefficient].every(Number.isFinite)) {
      result.textContent = 'Enter valid finite numbers.';
      return;
    }

    result.textContent = 'Calculating…';
    try {
      const response = await fetch('/api/v1/calculator/evaluate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          formula_id: 'frontend-linear-sandbox',
          expression: {
            op: 'add',
            args: [
              {const: base},
              {op: 'mul', args: [{stat: 'physical_attack'}, {const: coefficient}]}
            ]
          },
          stats: {physical_attack: attack}
        })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Calculation failed');
      result.textContent = 'Expression result: ' + payload.value;
    } catch (error) {
      result.textContent = 'Could not calculate: ' + error.message;
    }
  });
}

loadAtlas();
setupCalculator();


async function setupSkillVersions(heroes) {
  const heroSelect = document.querySelector('#skill-hero-filter');
  const skillSearch = document.querySelector('#skill-search');
  const patchSelect = document.querySelector('#skill-patch-filter');
  const list = document.querySelector('#skill-version-list');
  const count = document.querySelector('#skill-version-count');
  if (!heroSelect || !skillSearch || !patchSelect || !list || !count) return;

  heroes.forEach(hero => {
    const option = document.createElement('option');
    option.value = hero.slug || hero.id;
    option.textContent = hero.name;
    heroSelect.append(option);
  });

  const formatParameter = parameter => {
    const values = Array.isArray(parameter.values_by_skill_level) ? parameter.values_by_skill_level : [];
    const valueText = values.length ? values.join(' → ') : 'No numeric value';
    const unit = parameter.unit ? ' ' + parameter.unit : '';
    const semantics = parameter.value_semantics === 'endpoints'
      ? ' · только опубликованные границы'
      : parameter.value_semantics === 'per_level'
        ? ' · значения по уровням'
        : ' · фиксированное значение';
    return parameter.key + ': ' + valueText + unit + semantics;
  };

  const renderRecords = records => {
    list.replaceChildren();
    count.textContent = records.length + ' записей';
    if (!records.length) {
      const empty = document.createElement('p');
      empty.className = 'empty';
      empty.textContent = 'По этому фильтру записей пока нет.';
      list.append(empty);
      return;
    }
    records.forEach(record => {
      const card = document.createElement('article');
      card.className = 'skill-record';
      const heading = document.createElement('div');
      heading.className = 'skill-record-heading';
      const title = document.createElement('strong');
      title.textContent = record.skill_name + ' · ' + record.hero_id;
      const patch = document.createElement('span');
      patch.className = 'skill-patch';
      patch.textContent = 'Патч ' + record.patch.version;
      heading.append(title, patch);
      const meta = document.createElement('p');
      meta.className = 'muted small';
      meta.textContent = record.patch.channel + ' · ' + record.patch.effective_from + ' · статус: ' + record.verification.status;
      const parameters = document.createElement('ul');
      parameters.className = 'skill-parameter-list';
      (record.parameters || []).forEach(parameter => {
        const item = document.createElement('li');
        item.textContent = formatParameter(parameter);
        parameters.append(item);
      });
      card.append(heading, meta, parameters);
      (record.sources || []).forEach(source => {
        if (!source.url) return;
        const link = document.createElement('a');
        link.href = source.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Источник';
        link.className = 'source-link';
        card.append(link);
      });
      list.append(card);
    });
  };

  let allRecords = [];
  const refresh = async () => {
    const params = new URLSearchParams();
    if (heroSelect.value) params.set('hero_id', heroSelect.value);
    if (patchSelect.value) params.set('patch', patchSelect.value);
    const response = await fetch('/api/v1/skill-versions?' + params.toString());
    if (!response.ok) throw new Error('Не удалось загрузить базу параметров');
    const payload = await response.json();
    allRecords = payload.data || [];
    const needle = skillSearch.value.trim().toLocaleLowerCase();
    renderRecords(needle
      ? allRecords.filter(record => (record.skill_name || '').toLocaleLowerCase().includes(needle))
      : allRecords);
  };

  [heroSelect, patchSelect].forEach(control => control.addEventListener('change', () => {
    refresh().catch(error => { list.textContent = error.message; });
  }));
  skillSearch.addEventListener('input', () => {
    const needle = skillSearch.value.trim().toLocaleLowerCase();
    renderRecords(needle
      ? allRecords.filter(record => (record.skill_name || '').toLocaleLowerCase().includes(needle))
      : allRecords);
  });
  await refresh();
}


async function setupMatchupCalculator() {
  const ids = ['attacker-hero','defender-hero','attacker-emblem','defender-emblem','attacker-spell','defender-spell'];
  if (!document.getElementById(ids[0])) return;
  const result = document.querySelector('#matchup-result');
  const [heroesPayload, itemsPayload, emblemsPayload, spellsPayload] = await Promise.all([
    fetch('/api/v1/heroes').then(r => r.json()),
    fetch('/api/v1/items').then(r => r.json()),
    fetch('/api/v1/emblems').then(r => r.json()),
    fetch('/api/v1/spells').then(r => r.json())
  ]);
  const heroes = heroesPayload.data || [];
  const items = itemsPayload.data || [];
  const emblems = emblemsPayload.data || [];
  const spells = spellsPayload.data || [];

  function fillSelect(select, rows, label, placeholder) {
    select.replaceChildren();
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = placeholder;
    select.append(empty);
    rows.forEach(row => {
      const option = document.createElement('option');
      option.value = row.record_id || row.slug || row.id;
      option.textContent = label(row);
      select.append(option);
    });
  }
  const byName = (a,b) => (a.name || '').localeCompare(b.name || '');
  ['attacker-hero','defender-hero'].forEach(id => fillSelect(document.getElementById(id), heroes, h => h.name, 'Выбери героя'));
  ['attacker-emblem','defender-emblem'].forEach(id => fillSelect(document.getElementById(id), emblems, e => e.name, 'Без эмблемы'));
  ['attacker-spell','defender-spell'].forEach(id => fillSelect(document.getElementById(id), spells, s => s.name + ' · ' + s.cooldown_seconds + ' сек.', 'Без заклинания'));
  const sortedItems = [...items].sort(byName);
  ['attacker-items','defender-items'].forEach(containerId => {
    const container = document.getElementById(containerId);
    for (let slot = 1; slot <= 6; slot++) {
      const label = document.createElement('label');
      label.textContent = 'Предмет ' + slot;
      const select = document.createElement('select');
      select.className = 'build-item-select';
      select.dataset.slot = String(slot);
      fillSelect(select, sortedItems, item => item.name, 'Пустой слот');
      label.append(select);
      container.append(label);
    }
  });
  const skillSelect = document.querySelector('#matchup-skill');
  const attackerHero = document.querySelector('#attacker-hero');
  async function refreshSkills() {
    skillSelect.replaceChildren();
    const selectedHero = attackerHero.value;
    if (!selectedHero) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = 'Сначала выбери атакующего героя';
      skillSelect.append(option);
      return;
    }
    const payload = await fetch('/api/v1/skill-versions?hero_id=' + encodeURIComponent(selectedHero)).then(r => r.json());
    const rows = payload.data || [];
    fillSelect(skillSelect, rows, row => row.skill_name + ' · патч ' + row.patch.version + ' · ' + row.verification.status, 'Без навыка');
    rows.forEach((row, index) => { if (index === rows.length - 1) skillSelect.value = row.record_id; });
  }
  attackerHero.addEventListener('change', () => refreshSkills().catch(error => { result.textContent = error.message; }));
  await refreshSkills();

  function readSide(prefix) {
    return {
      hero_id: document.getElementById(prefix + '-hero').value,
      emblem_id: document.getElementById(prefix + '-emblem').value || null,
      spell_id: document.getElementById(prefix + '-spell').value || null,
      item_ids: [...document.querySelectorAll('#' + prefix + '-items select')].map(x => x.value).filter(Boolean),
      buffs: {
        blue: document.getElementById(prefix + '-blue').checked,
        red: document.getElementById(prefix + '-red').checked
      },
      total_physical_attack: Number(document.getElementById(prefix + '-pa')?.value || 0),
      total_magic_power: Number(document.getElementById(prefix + '-mp')?.value || 0),
      total_hp: Number(document.getElementById(prefix + '-hp')?.value || 0),
      physical_defense: Number(document.getElementById(prefix + '-pd')?.value || 0),
      magic_defense: Number(document.getElementById(prefix + '-md')?.value || 0)
    };
  }
  document.querySelector('#matchup-calculate').addEventListener('click', async () => {
    const attacker = readSide('attacker');
    const defender = readSide('defender');
    if (!attacker.hero_id || !defender.hero_id) {
      result.textContent = 'Выбери героя для обеих сторон.';
      return;
    }
    result.textContent = 'Считаю параметры сборок…';
    try {
      const response = await fetch('/api/v1/calculator/matchup-preview', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          attacker, defender,
          skill_record_id: skillSelect.value || null,
          endpoint: document.querySelector('#matchup-endpoint').value
        })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Ошибка расчёта');
      const lines = [];
      lines.push(payload.attacker.hero.name + ' → ' + payload.defender.hero.name);
      lines.push('Атакующий: ' + payload.attacker.items.length + ' предметов · эмблема: ' + (payload.attacker.emblem?.name || 'нет') + ' · заклинание: ' + (payload.attacker.spell?.name || 'нет'));
      lines.push('Противник: ' + payload.defender.items.length + ' предметов · эмблема: ' + (payload.defender.emblem?.name || 'нет') + ' · заклинание: ' + (payload.defender.spell?.name || 'нет'));
      lines.push('Атака: ' + JSON.stringify(payload.attacker.stats));
      lines.push('Защита противника: ' + JSON.stringify(payload.defender.defenses));
      if (payload.skill) {
        lines.push('Навык: ' + payload.skill.skill_name + ' · патч ' + payload.skill.patch.version + ' · ' + payload.skill.verification.status);
        lines.push(payload.damage_before_defense === null ? (payload.skill.damage_note || 'Для этого навыка пока нет достаточных числовых параметров.') : 'Расчётный урон до защиты: ' + Number(payload.damage_before_defense).toFixed(2));
        lines.push(payload.skill.note);
      } else {
        lines.push('Навык не выбран — показаны только параметры сборок.');
      }
      lines.push(payload.buff_note);
      lines.push(payload.spell_note);
      result.textContent = lines.join('\n');
    } catch (error) {
      result.textContent = 'Не удалось рассчитать: ' + error.message;
    }
  });
}

setupMatchupCalculator().catch(error => console.error(error));
