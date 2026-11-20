import test from 'node:test';
import assert from 'node:assert/strict';
import { PeriodAveragesPage } from '../../app/static/js/period-averages-page.js';

function view() {
  return { rendered: [], messages: [], clears: 0, region: { value: '' },
    readQuery(countries) { return { indicatorCode: 'IM_DTP3', firstYear: 2000, lastYear: 2023, periodYears: 5, countryIso3s: countries }; },
    showStatus(message) { this.messages.push(message); },
    clearResults() { this.clears++; },
    renderHeading(indicator) { this.rendered.push(indicator.name); },
    renderTable() {}, renderChart() {}, renderCountries() {},
  };
}

function report(name) {
  return { indicator: { name, unit: '%' }, periods: [{ label: '2000–2004' }],
    series: [{ country_iso3: 'ROU', country_name: 'Romania', averages: [90] }] };
}

test('late responses cannot overwrite newer filters even if a transport ignores abort', async () => {
  const original = globalThis.fetch;
  const requests = [];
  globalThis.fetch = (url, options) => new Promise(resolve => requests.push({ resolve, signal: options.signal }));
  try {
    const page = new PeriodAveragesPage(view()); page.selected = ['ROU'];
    const older = page.refresh(); const newer = page.refresh();
    assert.equal(requests[0].signal.aborted, true);
    requests[1].resolve(Response.json(report('Latest'))); await newer;
    requests[0].resolve(Response.json(report('Outdated'))); await older;
    assert.deepEqual(page.view.rendered, ['Latest']);
  } finally { globalThis.fetch = original; }
});

test('no selection invalid years and failed requests clear old results', async () => {
  const original = globalThis.fetch;
  try {
    const page = new PeriodAveragesPage(view());
    await page.refresh(); assert.match(page.view.messages.at(-1), /at least one/);
    page.selected = ['ROU'];
    const valid = page.view.readQuery;
    page.view.readQuery = () => ({ firstYear: 2023, lastYear: 2000 });
    await page.refresh(); assert.match(page.view.messages.at(-1), /ordered year range/);
    page.view.readQuery = valid;
    globalThis.fetch = async () => Response.json({ detail: 'Database unavailable' }, { status: 503 });
    await page.refresh();
    assert.equal(page.view.clears, 3);
    assert.match(page.view.messages.at(-1), /Database unavailable/);
  } finally { globalThis.fetch = original; }
});

test('outdated region lookups cannot replace the latest country choices', async () => {
  const original = globalThis.fetch;
  const requests = [];
  globalThis.fetch = () => new Promise(resolve => requests.push(resolve));
  try {
    const page = new PeriodAveragesPage(view());
    page.refresh = async () => {};
    const older = page.loadCountries(); const newer = page.loadCountries();
    requests[1](Response.json([{ iso3: 'FRA', name: 'France' }])); await newer;
    requests[0](Response.json([{ iso3: 'KEN', name: 'Kenya' }])); await older;
    assert.deepEqual(page.selected, ['FRA']);
  } finally { globalThis.fetch = original; }
});
