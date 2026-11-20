/** Network boundary: only this module calls fetch. */
export class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function errorDetail(response) {
  try {
    const { detail } = await response.json();
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map(item => `${item.loc?.at(-1) ?? 'Request'}: ${item.msg}`).join('; ');
  } catch { /* A proxy can return HTML instead of a JSON error. */ }
  return `Request failed (${response.status}).`;
}

async function getJson(path, params = new URLSearchParams(), signal) {
  const query = params.toString();
  const response = await fetch(`/api${path}${query ? `?${query}` : ''}`, {
    headers: { Accept: 'application/json' }, signal,
  });
  if (!response.ok) throw new ApiError(response.status, await errorDetail(response));
  return response.json();
}

export const fetchRegions = signal => getJson('/regions', undefined, signal);
export const fetchIndicators = signal => getJson('/indicators', undefined, signal);
export const fetchCountries = (region, signal) => getJson('/countries',
  new URLSearchParams(region ? { region } : {}), signal);

export function fetchPeriodAverages(query, signal) {
  const params = new URLSearchParams({ first_year: String(query.firstYear), last_year: String(query.lastYear),
    period_years: String(query.periodYears) });
  for (const code of query.countryIso3s) params.append('country', code);
  return getJson(`/indicators/${encodeURIComponent(query.indicatorCode)}/period-averages`, params, signal);
}
