import test from 'node:test';
import assert from 'node:assert/strict';
import { ColorSlots, changeSelection, initialCountries, toChart, toTable, validateYears } from '../../app/static/js/period-averages-model.js';

test('country defaults prefer project comparisons and keep a valid previous selection', () => {
  const countries = ['DEU', 'FRA', 'ROU', 'GBR', 'POL', 'SWE'].map(iso3 => ({ iso3 }));
  assert.deepEqual(initialCountries(countries), ['ROU', 'FRA', 'DEU', 'GBR', 'POL']);
  assert.deepEqual(initialCountries(countries, ['KEN', 'SWE']), ['SWE']);
  assert.deepEqual(initialCountries([]), []);
});

test('selection enforces eight unique countries without preventing removal', () => {
  const codes = Array.from({ length: 8 }, (_, i) => `C${i}`);
  assert.throws(() => changeSelection(codes, 'C8', true), /at most 8/);
  assert.equal(changeSelection(codes, 'C0', true).length, 8);
  assert.equal(changeSelection(codes, 'C0', false).length, 7);
});

test('colors stay stable when countries are added removed or reordered', () => {
  const colors = new ColorSlots();
  colors.update(['ROU', 'FRA']);
  const france = colors.slotOf('FRA');
  colors.update(['KEN', 'FRA']);
  assert.equal(colors.slotOf('FRA'), france);
  assert.equal(colors.slotOf('ROU'), undefined);
  assert.notEqual(colors.slotOf('KEN'), france);
  colors.update(['FRA', 'KEN']);
  assert.equal(colors.slotOf('FRA'), france);
});

test('invalid and unordered years are rejected before requesting data', () => {
  for (const years of [[2023, 2000], [0, 2023], [2000, 2101], [NaN, 2023], [2000.5, 2023]]) {
    assert.throws(() => validateYears(...years));
  }
  assert.doesNotThrow(() => validateYears(2023, 2023));
});

test('table and chart align periods and preserve null gaps and zero values', () => {
  const report = { indicator: { name: 'DTP3', unit: '%' }, periods: [{ label: '2000–2004' }, { label: '2005–2009' }],
    series: [{ country_iso3: 'ROU', country_name: 'Romania', averages: [0, null] }] };
  const colors = new ColorSlots(); colors.update(['ROU']);
  assert.deepEqual(toTable(report).rows[0].cells, [0, null]);
  const chart = toChart(report, colors);
  assert.deepEqual(chart.labels, ['2000–2004', '2005–2009']);
  assert.deepEqual(chart.lines[0].values, [0, null]);
  assert.equal(chart.yTitle, 'DTP3 (%)');
  assert.equal(chart.lines[0].colorSlot, 1);
});
