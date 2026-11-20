import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError, fetchCountries, fetchPeriodAverages } from '../../app/static/js/api-client.js';

test('encodes regions paths repeated countries and forwards cancellation', async () => {
  const original = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return Response.json([]); };
  try {
    const signal = new AbortController().signal;
    await fetchCountries('Europe & Central Asia', signal);
    await fetchPeriodAverages({ indicatorCode: 'A/B', firstYear: 2000, lastYear: 2023,
      periodYears: 5, countryIso3s: ['ROU', 'FRA'] }, signal);
    assert.equal(new URL(calls[0].url, 'http://local').searchParams.get('region'), 'Europe & Central Asia');
    assert.match(calls[1].url, /A%2FB/);
    assert.deepEqual(new URL(calls[1].url, 'http://local').searchParams.getAll('country'), ['ROU', 'FRA']);
    assert.equal(calls[1].options.signal, signal);
    assert.equal(calls[1].options.headers.Accept, 'application/json');
  } finally { globalThis.fetch = original; }
});

test('HTTP errors and non-JSON proxy failures become readable ApiErrors', async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async () => Response.json({ detail: [{ loc: ['query', 'period_years'], msg: 'Invalid period' }] }, { status: 422 });
    await assert.rejects(fetchCountries(''), error => error instanceof ApiError && error.status === 422 && /period_years/.test(error.message));
    globalThis.fetch = async () => new Response('<h1>Unavailable</h1>', { status: 503 });
    await assert.rejects(fetchCountries(''), /Request failed \(503\)/);
  } finally { globalThis.fetch = original; }
});
