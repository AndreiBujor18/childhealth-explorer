/** DOM-only presentation. API labels are always textContent, never HTML. */
export class PeriodAveragesView {
  constructor(root) {
    this.root = root;
    this.indicator = root.querySelector('#indicator');
    this.region = root.querySelector('#region');
    this.period = root.querySelector('#period-years');
    this.firstYear = root.querySelector('#first-year');
    this.lastYear = root.querySelector('#last-year');
    this.countries = root.querySelector('#country-list');
    this.summary = root.querySelector('#country-summary');
    this.status = root.querySelector('#status');
    this.results = root.querySelector('#average-results');
    this.table = root.querySelector('#averages-table');
    this.canvas = root.querySelector('#averages-chart');
    this.chart = null;
    this.numberFormat = new Intl.NumberFormat('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  setOptions(select, options, value) {
    select.replaceChildren(...options.map(item => {
      const option = document.createElement('option');
      option.value = item.value;
      option.textContent = item.label;
      return option;
    }));
    select.value = value;
    select.disabled = false;
  }

  renderFilters(indicators, regions, defaults) {
    this.setOptions(this.indicator, indicators.map(item => ({ value: item.code, label: item.name })), defaults.indicator);
    this.setOptions(this.region, [{ value: '', label: 'All regions' },
      ...regions.map(region => ({ value: region, label: region }))], defaults.region);
    this.setOptions(this.period, defaults.periods.map(value => ({ value, label: `${value} ${value === 1 ? 'year' : 'years'}` })), 5);
    this.firstYear.disabled = this.lastYear.disabled = false;
  }

  renderCountries(countries, selected) {
    const focusedCode = this.countries.contains(document.activeElement) ? document.activeElement.value : null;
    this.countries.replaceChildren(...countries.map(country => {
      const li = document.createElement('li');
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = 'checkbox'; input.value = country.iso3; input.checked = selected.includes(country.iso3);
      const text = document.createElement('span'); text.textContent = country.name;
      label.append(input, text); li.append(label); return li;
    }));
    this.summary.textContent = selected.length
      ? `${selected.length} ${selected.length === 1 ? 'country' : 'countries'} selected` : 'Choose countries';
    if (focusedCode) [...this.countries.querySelectorAll('input')]
      .find(input => input.value === focusedCode)?.focus({ preventScroll: true });
  }

  showStatus(message, { isError = false } = {}) {
    this.status.textContent = message;
    this.status.classList.toggle('status-failed', isError);
  }

  onFilters({ refresh, region, country }) {
    for (const control of [this.indicator, this.period, this.firstYear, this.lastYear]) control.addEventListener('change', refresh);
    this.region.addEventListener('change', region);
    this.countries.addEventListener('change', event => {
      if (event.target.matches('input[type="checkbox"]')) country(event.target.value, event.target.checked);
    });
  }

  readQuery(countryIso3s) {
    return { indicatorCode: this.indicator.value, firstYear: Number(this.firstYear.value),
      lastYear: Number(this.lastYear.value), periodYears: Number(this.period.value), countryIso3s };
  }

  renderHeading(indicator) {
    this.root.querySelector('#report-title').textContent = indicator.name;
    this.root.querySelector('#report-unit').textContent = indicator.unit ?? 'Unit not supplied by source';
    this.results.hidden = false;
  }

  renderTable(model) {
    const caption = document.createElement('caption');
    caption.textContent = `${model.caption}. Arithmetic means of available annual observations.`;
    caption.className = 'sr-only';
    const head = document.createElement('thead');
    const header = document.createElement('tr');
    for (const [index, label] of ['Country', ...model.periods].entries()) {
      const cell = document.createElement('th'); cell.scope = 'col'; cell.textContent = label;
      if (index) cell.className = 'number';
      header.append(cell);
    }
    head.append(header);
    const body = document.createElement('tbody');
    for (const row of model.rows) {
      const tr = document.createElement('tr');
      const name = document.createElement('th'); name.scope = 'row'; name.className = 'series-country';
      name.textContent = row.name; tr.append(name);
      for (const value of row.cells) {
        const cell = document.createElement('td'); cell.className = 'number numeric';
        cell.textContent = value === null ? '—' : this.numberFormat.format(value); tr.append(cell);
      }
      body.append(tr);
    }
    this.table.replaceChildren(caption, head, body);
  }

  renderChart(model) {
    this.chart?.destroy(); this.chart = null;
    const notice = this.root.querySelector('#chart-notice');
    const available = typeof window.Chart === 'function';
    this.canvas.parentElement.hidden = !available;
    notice.hidden = available;
    if (!available) return;
    const styles = getComputedStyle(this.root);
    const ink = getComputedStyle(document.body).color;
    const grid = styles.getPropertyValue('--chart-grid').trim();
    this.canvas.setAttribute('aria-label', `${model.yTitle}. ${model.lines.map(line => line.label).join(', ')}. Exact values follow in the table.`);
    this.chart = new window.Chart(this.canvas, {
      type: 'line',
      data: { labels: model.labels, datasets: model.lines.map(line => ({ label: line.label,
        data: line.values, borderColor: styles.getPropertyValue(`--series-${line.colorSlot}`).trim(),
        backgroundColor: styles.getPropertyValue(`--series-${line.colorSlot}`).trim(),
        borderWidth: 2, pointRadius: 3, pointHoverRadius: 5, tension: 0, spanGaps: false })) },
      options: { responsive: true, maintainAspectRatio: false, animation: false,
        plugins: { legend: { position: 'bottom', labels: { color: ink, usePointStyle: true, padding: 22 } } },
        scales: { x: { ticks: { color: ink, maxRotation: 0, autoSkip: true }, grid: { display: false } },
          y: { title: { display: true, text: model.yTitle, color: ink }, ticks: { color: ink }, grid: { color: grid } } } },
    });
  }

  clearResults() {
    this.results.hidden = true;
    this.table.replaceChildren();
    this.chart?.destroy(); this.chart = null;
  }
}
