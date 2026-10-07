/** Display formatting only: exported numbers are never recalculated. */
const typographic = (text: string) => text.replace(/^-/, '−').replace(/(\s)-/g, '$1−');

export function num(value: number, digits = 3): string {
  return typographic(value.toLocaleString('en-US', { maximumFractionDigits: digits }));
}
export function fixed(value: number, digits: number): string {
  return typographic(value.toFixed(digits));
}
/** Full-precision record notation, kept machine-like for ledgers. */
export function sci(value: number | boolean, digits = 6): string {
  return typeof value === 'number' ? value.toExponential(digits) : String(value);
}
export function full(value: number | boolean): string {
  return typeof value === 'number' ? num(value, 12) : String(value);
}
