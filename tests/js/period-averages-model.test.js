import test from 'node:test';
import assert from 'node:assert/strict';
import { ColorSlots, changeSelection, initialCountries, validateYears } from '../../app/static/js/period-averages-model.js';

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
