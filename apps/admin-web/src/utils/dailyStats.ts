import type { DailyStat } from '../mocks/data';

export interface DailyStatsSummary {
  installs: number;
  regs: number;
  applies: number;
  disburses: number;
  repayments: number;
  amount: number;
}

export const summarizeDailyStats = (list: DailyStat[]): DailyStatsSummary =>
  list.reduce<DailyStatsSummary>(
    (acc, item) => ({
      installs: acc.installs + item.installs,
      regs: acc.regs + item.regs,
      applies: acc.applies + item.applies,
      disburses: acc.disburses + item.disburses,
      repayments: acc.repayments + item.repayments,
      amount: acc.amount + item.amount
    }),
    { installs: 0, regs: 0, applies: 0, disburses: 0, repayments: 0, amount: 0 }
  );
