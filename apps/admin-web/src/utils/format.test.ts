import { describe, it, expect } from 'vitest';
import { maskPhone, formatCurrency } from './format';
import { summarizeDailyStats } from './dailyStats';

describe('format utils', () => {
  it('masks phone numbers with digits preserved', () => {
    const masked = maskPhone('+233-553-001-123');
    expect(masked).toMatch(/\*/);
    expect(masked.startsWith('+233')).toBe(true);
    expect(masked.endsWith('23')).toBe(true);
  });

  it('formats currency safely', () => {
    expect(formatCurrency(150)).toBe('₵150');
    expect(formatCurrency(12345)).toBe('₵12,345');
  });

  it('summarizes daily stats', () => {
    const summary = summarizeDailyStats([
      { date: '2025-10-20', installs: 48, regs: 1, logins: 0, applies: 27, disburses: 15, repayments: 15, amount: 93800 },
      { date: '2025-10-19', installs: 197, regs: 7, logins: 7, applies: 110, disburses: 54, repayments: 25, amount: 20195 }
    ]);
    expect(summary).toEqual({
      installs: 245,
      regs: 8,
      applies: 137,
      disburses: 69,
      repayments: 40,
      amount: 113995
    });
  });
});
