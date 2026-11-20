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
    this.countries.replaceChildren(...countries.map(country => {
      const li = document.createElement('li');
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = 'checkbox'; input.value = country.iso3; input.checked = selected.includes(country.iso3);
      const text = document.createElement('span'); text.textContent = country.name;
      label.append(input, text); li.append(label); return li;
    }));
    this.summary.textContent = selected.length ? `${selected.length} countries selected` : 'Choose countries';
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
}
