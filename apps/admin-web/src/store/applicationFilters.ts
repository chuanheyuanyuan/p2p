import dayjs from 'dayjs';
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ApplicationQuery } from '../services/api';

type FilterStore = ApplicationQuery & {
  setFilters: (filters: ApplicationQuery) => void;
  reset: () => void;
};

const defaultRange = [dayjs().subtract(7, 'day'), dayjs()];
const initialFilters: ApplicationQuery = {
  page: 1,
  pageSize: 10,
  startDate: defaultRange[0].format('YYYY-MM-DD'),
  endDate: defaultRange[1].format('YYYY-MM-DD')
};

export const useApplicationFilterStore = create<FilterStore>()(
  persist(
    (set) => ({
      ...initialFilters,
      setFilters: (filters) => set({ ...filters }),
      reset: () => set({ ...initialFilters })
    }),
    {
      name: 'admin-application-filters',
      storage: createJSONStorage(() => localStorage)
    }
  )
);
