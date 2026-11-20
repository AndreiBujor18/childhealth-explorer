/** Page controller: requests, event wiring and stale-response cancellation. */
import { fetchCountries, fetchIndicators, fetchPeriodAverages, fetchRegions } from './api-client.js';
import { DEFAULT_INDICATOR, DEFAULT_REGION, PERIOD_LENGTHS, changeSelection,
  initialCountries, validateYears } from './period-averages-model.js';
import { PeriodAveragesView } from './period-averages-view.js';

export class PeriodAveragesPage {
  constructor(view) {
    this.view = view;
    this.selected = [];
    this.countries = [];
    this.pendingRequest = null;
    this.countryRequest = null;
  }

  async start() {
    try {
      const [indicators, regions] = await Promise.all([fetchIndicators(), fetchRegions()]);
      if (!indicators.length) throw new Error('No indicators are available. Import source data first.');
      this.view.renderFilters(indicators, regions, {
        indicator: indicators.some(item => item.code === DEFAULT_INDICATOR) ? DEFAULT_INDICATOR : indicators[0].code,
        region: regions.includes(DEFAULT_REGION) ? DEFAULT_REGION : '', periods: PERIOD_LENGTHS,
      });
      this.view.onFilters({ refresh: () => this.refresh(), region: () => this.loadCountries(),
        country: (code, checked) => this.selectCountry(code, checked) });
      await this.loadCountries();
    } catch (error) {
      this.view.showStatus(`Could not load the page: ${error.message}`, { isError: true });
    }
  }

  async loadCountries() {
    this.countryRequest?.abort();
    this.pendingRequest?.abort(); this.pendingRequest = null;
    const request = new AbortController();
    this.countryRequest = request;
    this.countries = []; this.view.renderCountries([], []);
    this.view.showStatus('Loading countries…');
    try {
      const countries = await fetchCountries(this.view.region.value, request.signal);
      if (this.countryRequest !== request) return;
      this.countries = countries;
      this.selected = initialCountries(countries, this.selected);
      this.view.renderCountries(countries, this.selected);
      this.countryRequest = null;
      await this.refresh();
    } catch (error) {
      if (this.countryRequest !== request || error.name === 'AbortError') return;
      this.countryRequest = null;
      this.view.showStatus(`Could not load countries: ${error.message}`, { isError: true });
    }
  }

  selectCountry(code, checked) {
    try { this.selected = changeSelection(this.selected, code, checked); }
    catch (error) {
      this.view.renderCountries(this.countries, this.selected);
      this.view.showStatus(error.message, { isError: true }); return;
    }
    this.view.renderCountries(this.countries, this.selected);
    this.refresh();
  }

  async refresh() {
    this.pendingRequest?.abort(); this.pendingRequest = null;
    if (this.countryRequest) return;
    if (!this.selected.length) { this.view.showStatus('Choose at least one country.'); return; }
    const query = this.view.readQuery([...this.selected]);
    try { validateYears(query.firstYear, query.lastYear); }
    catch (error) { this.view.showStatus(error.message, { isError: true }); return; }
    const request = new AbortController();
    this.pendingRequest = request;
    this.view.showStatus('Loading averages…');
    try {
      const report = await fetchPeriodAverages(query, request.signal);
      if (this.pendingRequest !== request) return;
      this.report = report;
      this.view.showStatus(`${report.series.length} countries · ${report.periods.length} periods. Data loaded.`);
    } catch (error) {
      if (this.pendingRequest !== request || error.name === 'AbortError') return;
      this.view.showStatus(`Could not load the data: ${error.message}`, { isError: true });
    }
  }
}

const root = document.querySelector('#averages-app');
if (root) new PeriodAveragesPage(new PeriodAveragesView(root)).start();
