import { useState } from 'react';
import type { ActiveSeriesInfo, GapRowState, SuggestionResult } from '../types';

interface Props {
  dataFile: string;
}

export default function DataPage({ dataFile }: Props) {
  const [scanning, setScanning] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  const [activeSeries, setActiveSeries] = useState<ActiveSeriesInfo[] | null>(null);
  const [dataLastDate, setDataLastDate] = useState<string | null>(null);
  const [rows, setRows] = useState<GapRowState[]>([]);
  const [apiKey, setApiKey] = useState('');
  const [filterSeries, setFilterSeries] = useState<string>('all');

  async function handleScan() {
    setScanning(true);
    setError(null);
    setSaveMsg(null);
    setActiveSeries(null);
    setRows([]);
    try {
      const params = new URLSearchParams({ dataFile });
      const resp = await fetch(`/api/data/gaps?${params}`);
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
      }
      const result = await resp.json() as { activeSeries: ActiveSeriesInfo[]; gaps: { series: string; date: string }[]; dataLastDate: string };
      setActiveSeries(result.activeSeries);
      setDataLastDate(result.dataLastDate);
      setFilterSeries('all');
      setRows(result.gaps.map(g => ({
        series: g.series,
        date: g.date,
        suggested: null,
        inputValue: '',
        status: 'pending',
      })));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setScanning(false);
    }
  }

  async function handleFetchSuggestions() {
    if (!apiKey.trim()) { setError('Enter a Barchart API key first.'); return; }
    setFetching(true);
    setError(null);
    const pending = rows.filter(r => r.status === 'pending');
    try {
      const resp = await fetch('/api/data/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gaps: pending.map(r => ({ series: r.series, date: r.date })), apiKey }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
      }
      const suggestions = await resp.json() as SuggestionResult[];
      const sugMap = new Map<string, SuggestionResult>();
      for (const s of suggestions) sugMap.set(`${s.series}|${s.date}`, s);

      setRows(prev => prev.map(r => {
        const key = `${r.series}|${r.date}`;
        const sug = sugMap.get(key);
        if (!sug) return r;
        return {
          ...r,
          suggested: sug.value,
          suggestionError: sug.error,
          inputValue: sug.value != null ? String(sug.value) : r.inputValue,
        };
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setFetching(false);
    }
  }

  function approveAll() {
    setRows(prev => prev.map(r => {
      if (r.suggested == null && r.inputValue === '') return r;
      const val = r.inputValue !== '' ? r.inputValue : String(r.suggested);
      return { ...r, inputValue: val, status: 'approved' };
    }));
  }

  function rejectAll() {
    setRows(prev => prev.map(r => ({ ...r, status: 'rejected' })));
  }

  function setRowStatus(series: string, date: string, status: GapRowState['status']) {
    setRows(prev => prev.map(r => r.series === series && r.date === date ? { ...r, status } : r));
  }

  function setRowValue(series: string, date: string, value: string) {
    setRows(prev => prev.map(r => r.series === series && r.date === date ? { ...r, inputValue: value } : r));
  }

  async function handleSave() {
    const approved = rows.filter(r => r.status === 'approved' && r.inputValue !== '');
    if (approved.length === 0) { setError('No approved entries to save.'); return; }
    setSaving(true);
    setError(null);
    setSaveMsg(null);
    try {
      const edits = approved.map(r => ({ series: r.series, date: r.date, value: parseFloat(r.inputValue) }));
      const resp = await fetch('/api/data/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ edits, dataFile }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
      }
      const result = await resp.json() as { saved: number };
      setSaveMsg(`Saved ${result.saved} entr${result.saved === 1 ? 'y' : 'ies'} to file.`);
      // Remove saved rows
      const savedKeys = new Set(approved.map(r => `${r.series}|${r.date}`));
      setRows(prev => prev.filter(r => !savedKeys.has(`${r.series}|${r.date}`)));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  const seriesOptions = activeSeries ? ['all', ...activeSeries.map(s => s.name)] : [];
  const visibleRows = filterSeries === 'all' ? rows : rows.filter(r => r.series === filterSeries);
  const approvedCount = rows.filter(r => r.status === 'approved').length;
  const hasSuggestions = rows.some(r => r.suggested != null);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-1">Data Manager</h2>
        <p className="text-sm text-gray-500">Scan for missing settlement prices in active contracts and write approved values back to the data file.</p>
      </div>

      {/* Scan bar */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={handleScan}
          disabled={scanning}
          className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
        >
          {scanning ? 'Scanning…' : 'Scan for Gaps'}
        </button>
        {dataLastDate && (
          <span className="text-xs text-gray-500">Last date in file: <span className="font-mono text-gray-700">{dataLastDate}</span></span>
        )}
      </div>

      {error && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">{error}</div>
      )}
      {saveMsg && (
        <div className="mb-4 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-3">{saveMsg}</div>
      )}

      {/* Active series summary */}
      {activeSeries && (
        <div className="mb-6 bg-white rounded-xl border border-gray-100 shadow-sm p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Active Contracts</h3>
          {activeSeries.length === 0 ? (
            <p className="text-sm text-gray-400">No active contracts found within the last 60 days.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {activeSeries.map(s => (
                <div key={s.name} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 bg-gray-50">
                  <span className="text-sm font-mono font-medium text-gray-700">{s.name}</span>
                  <span className="text-xs text-gray-400">expires {s.expiry}</span>
                  {s.gapCount > 0 ? (
                    <span className="text-xs font-semibold text-amber-600 bg-amber-50 border border-amber-200 rounded px-1.5">{s.gapCount} gap{s.gapCount !== 1 ? 's' : ''}</span>
                  ) : (
                    <span className="text-xs text-green-600 bg-green-50 border border-green-200 rounded px-1.5">up to date</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Gaps table */}
      {rows.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          {/* Table toolbar */}
          <div className="flex flex-wrap items-center gap-3 p-4 border-b border-gray-100">
            <span className="text-sm font-semibold text-gray-700">
              {rows.length} gap{rows.length !== 1 ? 's' : ''}
              {approvedCount > 0 && <span className="ml-1 text-indigo-600">· {approvedCount} approved</span>}
            </span>

            {/* Series filter */}
            <select
              value={filterSeries}
              onChange={e => setFilterSeries(e.target.value)}
              className="text-xs border border-gray-200 rounded px-2 py-1 bg-white"
            >
              {seriesOptions.map(s => <option key={s} value={s}>{s === 'all' ? 'All series' : s}</option>)}
            </select>

            <div className="flex-1" />

            {/* Barchart fetch */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Barchart API key"
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
                className="text-xs border border-gray-200 rounded px-2 py-1 w-40 font-mono bg-white focus:outline-none focus:ring-1 focus:ring-indigo-400"
              />
              <button
                onClick={handleFetchSuggestions}
                disabled={fetching || !apiKey.trim()}
                className="text-xs px-3 py-1 rounded-lg bg-gray-100 border border-gray-200 text-gray-700 hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                {fetching ? 'Fetching…' : 'Fetch Suggestions'}
              </button>
            </div>

            {/* Bulk actions */}
            {hasSuggestions && (
              <button onClick={approveAll} className="text-xs px-3 py-1 rounded-lg bg-green-50 border border-green-200 text-green-700 hover:bg-green-100 transition-colors">
                Approve All
              </button>
            )}
            <button onClick={rejectAll} className="text-xs px-3 py-1 rounded-lg bg-red-50 border border-red-200 text-red-600 hover:bg-red-100 transition-colors">
              Reject All
            </button>
            <button
              onClick={handleSave}
              disabled={saving || approvedCount === 0}
              className="text-xs px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {saving ? 'Saving…' : `Save to File (${approvedCount})`}
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="text-left px-4 py-2 font-medium">Series</th>
                  <th className="text-left px-4 py-2 font-medium">Date</th>
                  <th className="text-left px-4 py-2 font-medium">Suggested</th>
                  <th className="text-left px-4 py-2 font-medium w-32">Value</th>
                  <th className="text-center px-4 py-2 font-medium w-28">Action</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map(row => {
                  const key = `${row.series}|${row.date}`;
                  const isApproved = row.status === 'approved';
                  const isRejected = row.status === 'rejected';
                  return (
                    <tr key={key} className={`border-b border-gray-50 ${isRejected ? 'opacity-40' : ''}`}>
                      <td className="px-4 py-2 font-mono text-xs text-gray-700">{row.series}</td>
                      <td className="px-4 py-2 font-mono text-xs text-gray-600">{row.date}</td>
                      <td className="px-4 py-2 text-xs">
                        {row.suggested != null ? (
                          <span className="font-mono text-gray-700">{row.suggested.toFixed(3)}</span>
                        ) : row.suggestionError ? (
                          <span className="text-red-400" title={row.suggestionError}>error</span>
                        ) : (
                          <span className="text-gray-300">—</span>
                        )}
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          step="0.001"
                          value={row.inputValue}
                          onChange={e => setRowValue(row.series, row.date, e.target.value)}
                          placeholder="enter value"
                          disabled={isRejected}
                          className="w-full text-xs border border-gray-200 rounded px-2 py-1 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-400 disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => setRowStatus(row.series, row.date, 'approved')}
                            title="Approve"
                            className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                              isApproved
                                ? 'bg-green-500 text-white border-green-500'
                                : 'bg-white text-gray-400 border-gray-200 hover:border-green-400 hover:text-green-600'
                            }`}
                          >
                            ✓
                          </button>
                          <button
                            onClick={() => setRowStatus(row.series, row.date, 'rejected')}
                            title="Reject"
                            className={`px-2 py-0.5 text-xs rounded border transition-colors ${
                              isRejected
                                ? 'bg-red-500 text-white border-red-500'
                                : 'bg-white text-gray-400 border-gray-200 hover:border-red-400 hover:text-red-600'
                            }`}
                          >
                            ✗
                          </button>
                          <button
                            onClick={() => setRowStatus(row.series, row.date, 'pending')}
                            title="Reset"
                            className="px-2 py-0.5 text-xs rounded border bg-white text-gray-300 border-gray-200 hover:text-gray-500 hover:border-gray-300 transition-colors"
                          >
                            ↺
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSeries && rows.length === 0 && (
        <div className="flex flex-col items-center justify-center h-40 text-gray-400 gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" className="w-10 h-10 text-gray-300">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">No gaps found — all active contracts are up to date.</p>
        </div>
      )}
    </div>
  );
}
