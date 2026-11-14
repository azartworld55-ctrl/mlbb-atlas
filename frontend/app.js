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
