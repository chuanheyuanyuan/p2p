import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ApplicationQuery } from '../services/api';

type FilterStore = ApplicationQuery & {
  setFilters: (filters: ApplicationQuery) => void;
  reset: () => void;
};

const initialFilters: ApplicationQuery = {
  page: 1,
  pageSize: 10
};

export const useApplicationFilterStore = create<FilterStore>()(
  persist(
    (set) => ({
      ...initialFilters,
      setFilters: (filters) => set({ ...filters }),
      reset: () => set(initialFilters)
    }),
    {
      name: 'admin-application-filters',
      storage: createJSONStorage(() => localStorage)
    }
  )
);
