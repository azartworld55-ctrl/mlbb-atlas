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

    render(heroes.data);\n    setupSkillVersions(heroes.data);
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
