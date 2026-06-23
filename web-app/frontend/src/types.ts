export interface SeriesData {
  dates: string[];
  values: (number | null)[];
}

export interface SpreadResult {
  farContract: string;
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export type ChartType = 'historical' | 'continuous' | 'monthly' | 'weekly' | 'individual';

export interface ButterflyResult {
  label: string;
  legs: [string, string, string];
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export interface AppConfig {
  displayMonths: Record<string, string>;
  regularMonthSets: Record<string, string[]>;
  commonButterflies: Record<string, [string, string, string]>;
  yearRange: { min: number; max: number };
}

export interface GapEntry {
  series: string;
  date: string;
}

export interface ActiveSeriesInfo {
  name: string;
  lastDate: string;
  expiry: string;
  gapCount: number;
}

export interface GapScanResult {
  activeSeries: ActiveSeriesInfo[];
  gaps: GapEntry[];
  dataLastDate: string;
}

export interface SuggestionResult {
  series: string;
  date: string;
  value: number | null;
  error?: string;
}

export type GapRowStatus = 'pending' | 'approved' | 'rejected';

export interface GapRowState {
  series: string;
  date: string;
  suggested: number | null;
  suggestionError?: string;
  inputValue: string;
  status: GapRowStatus;
}
