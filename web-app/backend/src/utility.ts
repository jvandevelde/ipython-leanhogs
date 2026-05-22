export const MONTHS: Record<string, number> = {
  G: 2,
  J: 4,
  K: 5,
  M: 6,
  N: 7,
  Q: 8,
  V: 10,
  Z: 12,
};

export const DISPLAY_MONTHS: Record<string, string> = {
  G: 'G - February',
  J: 'J - April',
  K: 'K - May',
  M: 'M - June',
  N: 'N - July',
  Q: 'Q - August',
  V: 'V - October',
  Z: 'Z - December',
};

export const REGULAR_MONTH_SETS: Record<string, string[]> = {
  G: ['J', 'K', 'M', 'N'],
  J: ['K', 'M', 'N', 'Q'],
  K: ['M', 'N', 'Q', 'V'],
  M: ['N', 'Q', 'V', 'Z'],
  N: ['Q', 'V', 'Z', 'G'],
  Q: ['V', 'Z', 'G', 'J'],
  V: ['Z', 'G', 'J', 'K'],
  Z: ['G', 'J', 'K', 'M'],
};

export const YEAR_MIN = 1998;

export const COMMON_BUTTERFLIES: Record<string, [string, string, string]> = {
  JKM: ['J', 'K', 'M'],
  KMN: ['K', 'M', 'N'],
  MNQ: ['M', 'N', 'Q'],
  NQV: ['N', 'Q', 'V'],
  QVZ: ['Q', 'V', 'Z'],
  VZG: ['V', 'Z', 'G'],
  ZGJ: ['Z', 'G', 'J'],
  GJK: ['G', 'J', 'K'],
  GJM: ['G', 'J', 'M'],
};
