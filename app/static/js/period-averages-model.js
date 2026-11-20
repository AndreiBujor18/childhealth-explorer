/** Plain selection and transformation rules: no DOM or network. */
export const DEFAULT_INDICATOR = 'IM_DTP3';
export const DEFAULT_REGION = 'Europe & Central Asia';
export const PERIOD_LENGTHS = [1, 3, 5, 10];
export const MAX_COUNTRIES = 8;

export function initialCountries(countries, previous = []) {
  const available = new Set(countries.map(country => country.iso3));
  const kept = previous.filter(code => available.has(code));
  if (kept.length) return kept.slice(0, MAX_COUNTRIES);
  const preferred = ['ROU', 'FRA', 'DEU', 'GBR', 'POL'].filter(code => available.has(code));
  return [...new Set([...preferred, ...countries.map(country => country.iso3)])].slice(0, 5);
}

export function changeSelection(selected, code, checked) {
  const next = checked ? [...new Set([...selected, code])] : selected.filter(item => item !== code);
  if (next.length > MAX_COUNTRIES) throw new Error(`Choose at most ${MAX_COUNTRIES} countries.`);
  return next;
}

export function validateYears(firstYear, lastYear) {
  if (!Number.isInteger(firstYear) || !Number.isInteger(lastYear)
      || firstYear < 1900 || lastYear > 2100 || firstYear > lastYear) {
    throw new Error('Enter an ordered year range between 1900 and 2100.');
  }
}

export class ColorSlots {
  constructor() { this.slots = new Map(); }
  update(codes) {
    if (new Set(codes).size > MAX_COUNTRIES) throw new Error('Too many chart countries.');
    for (const code of this.slots.keys()) if (!codes.includes(code)) this.slots.delete(code);
    for (const code of codes) {
      if (this.slots.has(code)) continue;
      const used = new Set(this.slots.values());
      const slot = Array.from({ length: MAX_COUNTRIES }, (_, index) => index + 1).find(value => !used.has(value));
      this.slots.set(code, slot);
    }
  }
  slotOf(code) { return this.slots.get(code); }
}
