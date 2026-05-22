export interface SeriesData {
  dates: string[];
  values: (number | null)[];
}

export interface SpreadResult {
  farContract: string;
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export interface CalculateRequest {
  near: string;
  years: number[];
  dataFile?: string;
}

export interface ButterflyResult {
  label: string;
  legs: [string, string, string];
  shifted: Record<string, SeriesData>;
  original: Record<string, SeriesData>;
}

export interface ButterflyRequest {
  combos: [string, string, string][];
  years: number[];
  dataFile?: string;
}
