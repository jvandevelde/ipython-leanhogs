import * as XLSX from 'xlsx';
import * as path from 'path';
import * as fs from 'fs';

export type RawData = Map<string, Map<string, number>>;

let cachedData: RawData | null = null;
let cachedFile: string | null = null;

export function loadData(dataFile?: string): RawData {
  const filePath = dataFile
    ? path.resolve(dataFile)
    : path.resolve(__dirname, '..', '..', '..', 'hog_settlements.xlsx');

  if (!fs.existsSync(filePath)) {
    throw new Error(`Data file not found: ${filePath}`);
  }

  if (cachedData && cachedFile === filePath) {
    return cachedData;
  }

  const workbook = XLSX.readFile(filePath, { cellDates: true });
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows: unknown[][] = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false, dateNF: 'yyyy-mm-dd' });

  const header = rows[0] as string[];
  // column 0 is dates, columns 1+ are contract names
  const result: RawData = new Map();

  for (let col = 1; col < header.length; col++) {
    const colName = String(header[col]).trim();
    if (!colName) continue;
    const series: Map<string, number> = new Map();
    for (let row = 1; row < rows.length; row++) {
      const rawDate = rows[row][0];
      const rawVal = rows[row][col];
      if (rawDate == null || rawVal == null || rawVal === '') continue;
      const dateStr = parseDateStr(rawDate);
      if (!dateStr) continue;
      const val = parseFloat(String(rawVal));
      if (!isNaN(val)) {
        series.set(dateStr, val);
      }
    }
    if (series.size > 0) result.set(colName, series);
  }

  cachedData = result;
  cachedFile = filePath;
  return result;
}

export function clearCache(): void {
  cachedData = null;
  cachedFile = null;
}

function parseDateStr(raw: unknown): string | null {
  if (!raw) return null;
  const s = String(raw).trim();
  // Try yyyy-mm-dd
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  // Try mm/dd/yyyy or dd/mm/yyyy via Date parse
  const d = new Date(s);
  if (!isNaN(d.getTime())) return toDateStr(d);
  return null;
}

export function toDateStr(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
