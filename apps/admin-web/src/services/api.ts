import { request } from './http';
import type {
  ApplicationDetail,
  ApplicationRecord,
  CollectionCase,
  CollectionCaseDetail,
  DailyStat,
  DashboardStats,
  FinanceDisbursement,
  FinanceRepayment,
  ReconciliationDiff,
  UserProfile
} from '../mocks/data';
import {
  applicationsMock,
  applicationDetailsMock,
  collectionCasesMock,
  collectionDetailsMock,
  adminAccountsMock,
  dashboardMock,
  defaultSessionMock,
  dailyStatsMock,
  financeDisbursementsMock,
  financeRepaymentsMock,
  reconciliationDiffsMock,
  userProfilesMock
} from '../mocks/data';
import type { LoginPayload, LoginResponse } from '../types/auth';

interface PaginatedResponse<T> {
  list: T[];
  total: number;
}

export interface ApplicationQuery {
  page?: number;
  pageSize?: number;
  loanId?: string;
  keyword?: string;
  phone?: string;
  startDate?: string;
  endDate?: string;
  status?: string;
  product?: string;
  level?: string;
  channel?: string;
  appVersion?: string;
  reviewer?: string;
  repeat?: 'yes' | 'no';
}

export async function adminLogin(payload: LoginPayload): Promise<LoginResponse> {
  try {
    return await request<LoginResponse>('/admin/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  } catch (error) {
    console.warn('adminLogin fallback to mock', error);
    const matched = adminAccountsMock.find(
      (account) => account.username === payload.username || account.email === payload.username
    );
    if (!matched || matched.password !== payload.password) {
      throw new Error('账号或密码错误');
    }
    return {
      accessToken: `mock-token-${matched.id}`,
      refreshToken: `mock-refresh-${matched.id}`,
      expiresIn: 3600,
      user: { id: matched.id, name: matched.name, email: matched.email, title: matched.title },
      roles: matched.roles,
      permissions: matched.permissions
    };
  }
}

export async function fetchCurrentSession(): Promise<LoginResponse> {
  try {
    return await request<LoginResponse>('/admin/v1/auth/me');
  } catch (error) {
    console.warn('fetchCurrentSession fallback', error);
    return defaultSessionMock;
  }
}

export async function fetchDashboardOverview(): Promise<DashboardStats> {
  try {
    return await request<DashboardStats>('/admin/v1/dashboard');
  } catch (error) {
    console.warn('fetchDashboardOverview fallback', error);
    return dashboardMock;
  }
}

export async function fetchApplications(params: ApplicationQuery): Promise<PaginatedResponse<ApplicationRecord>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        search.append(key, String(value));
      }
    });
    return await request(`/admin/v1/applications?${search.toString()}`);
  } catch (error) {
    console.warn('fetchApplications fallback to mock', error);
    return { list: applicationsMock, total: applicationsMock.length };
  }
}

export async function fetchApplicationById(id: string): Promise<ApplicationDetail> {
  try {
    return await request(`/admin/v1/applications/${id}`);
  } catch (error) {
    console.warn(`fetchApplicationById(${id}) fallback`, error);
    const detail = applicationDetailsMock[id];
    if (!detail) throw error;
    return detail;
  }
}

export async function fetchUserProfile(userId: string): Promise<UserProfile> {
  try {
    return await request(`/admin/v1/users/${userId}`);
  } catch (error) {
    console.warn(`fetchUserProfile(${userId}) fallback`, error);
    const profile = userProfilesMock[userId];
    if (!profile) throw error;
    return profile;
  }
}

export interface CollectionsQuery {
  page?: number;
  pageSize?: number;
  bucket?: string;
  assignee?: string;
}

export async function fetchCollectionCases(params: CollectionsQuery): Promise<PaginatedResponse<CollectionCase>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') search.append(key, String(value));
    });
    return await request(`/admin/v1/collections/cases?${search.toString()}`);
  } catch (error) {
    console.warn('fetchCollectionCases fallback', error);
    return { list: collectionCasesMock, total: collectionCasesMock.length };
  }
}

export async function fetchCollectionDetail(caseId: string): Promise<CollectionCaseDetail> {
  try {
    return await request(`/admin/v1/collections/cases/${caseId}`);
  } catch (error) {
    console.warn(`fetchCollectionDetail(${caseId}) fallback`, error);
    const detail = collectionDetailsMock[caseId];
    if (!detail) throw error;
    return detail;
  }
}

export interface DailyStatsQuery {
  startDate?: string;
  endDate?: string;
  channel?: string;
  repeat?: string;
  page?: number;
  pageSize?: number;
}

export interface FinanceQuery {
  status?: string;
  channel?: string;
  startDate?: string;
  endDate?: string;
  keyword?: string;
  type?: string;
}

export async function fetchDailyStats(params: DailyStatsQuery): Promise<PaginatedResponse<DailyStat>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') search.append(key, String(value));
    });
    return await request(`/admin/v1/reports/daily?${search.toString()}`);
  } catch (error) {
    console.warn('fetchDailyStats fallback', error);
    return {
      list: dailyStatsMock,
      total: dailyStatsMock.length
    };
  }
}

export async function exportApplications(params: ApplicationQuery): Promise<{ taskId: string }> {
  try {
    return await request<{ taskId: string }>('/admin/v1/applications/export', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  } catch (error) {
    console.warn('exportApplications fallback', error);
    return { taskId: `mock-application-export-${Date.now()}` };
  }
}

export async function exportDailyStats(params: DailyStatsQuery): Promise<{ taskId: string }> {
  try {
    return await request<{ taskId: string }>('/admin/v1/reports/daily/export', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  } catch (error) {
    console.warn('exportDailyStats fallback', error);
    return { taskId: `mock-export-${Date.now()}` };
  }
}

export async function fetchFinanceDisbursements(
  params: FinanceQuery
): Promise<PaginatedResponse<FinanceDisbursement>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) search.append(key, String(value));
    });
    return await request(`/admin/v1/finance/disbursements?${search.toString()}`);
  } catch (error) {
    console.warn('fetchFinanceDisbursements fallback', error);
    const list = financeDisbursementsMock.filter((item) => {
      if (params.status && item.status !== params.status) return false;
      if (params.channel && item.channel !== params.channel) return false;
      if (params.keyword) {
        const keyword = params.keyword.toLowerCase();
        if (!item.loanId.toLowerCase().includes(keyword) && !item.user.toLowerCase().includes(keyword)) {
          return false;
        }
      }
      if (!matchesDateRange(item.requestedAt, params.startDate, params.endDate)) return false;
      return true;
    });
    return { list, total: list.length };
  }
}

export async function retryFinanceDisbursement(disbursementId: string): Promise<{ success: boolean }> {
  try {
    return await request<{ success: boolean }>(`/admin/v1/finance/disbursements/${disbursementId}/retry`, {
      method: 'POST'
    });
  } catch (error) {
    console.warn(`retryFinanceDisbursement(${disbursementId}) fallback`, error);
    if (!financeDisbursementsMock.find((item) => item.id === disbursementId)) {
      throw new Error('未找到放款指令');
    }
    return { success: true };
  }
}

export async function fetchFinanceRepayments(
  params: FinanceQuery
): Promise<PaginatedResponse<FinanceRepayment>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) search.append(key, String(value));
    });
    return await request(`/admin/v1/finance/repayments?${search.toString()}`);
  } catch (error) {
    console.warn('fetchFinanceRepayments fallback', error);
    const list = financeRepaymentsMock.filter((item) => {
      if (params.status && item.status !== params.status) return false;
      if (params.channel && item.channel !== params.channel) return false;
      if (params.keyword) {
        const keyword = params.keyword.toLowerCase();
        if (!item.loanId.toLowerCase().includes(keyword) && !item.user.toLowerCase().includes(keyword)) {
          return false;
        }
      }
      if (!matchesDateRange(item.paidAt, params.startDate, params.endDate)) return false;
      return true;
    });
    return { list, total: list.length };
  }
}

export async function fetchReconciliationDiffs(
  params: FinanceQuery
): Promise<PaginatedResponse<ReconciliationDiff>> {
  try {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) search.append(key, String(value));
    });
    return await request(`/admin/v1/finance/reconciliation?${search.toString()}`);
  } catch (error) {
    console.warn('fetchReconciliationDiffs fallback', error);
    const list = reconciliationDiffsMock.filter((item) => {
      if (params.status && item.status !== params.status) return false;
      if (params.channel && item.channel !== params.channel) return false;
      if (params.type && item.type !== params.type) return false;
      if (!matchesDateRange(item.date, params.startDate, params.endDate)) return false;
      return true;
    });
    return { list, total: list.length };
  }
}

export async function exportReconciliation(params: FinanceQuery): Promise<{ taskId: string }> {
  try {
    return await request<{ taskId: string }>('/admin/v1/finance/reconciliation/export', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  } catch (error) {
    console.warn('exportReconciliation fallback', error);
    return { taskId: `mock-finance-export-${Date.now()}` };
  }
}

const matchesDateRange = (value: string, start?: string, end?: string) => {
  if (!start && !end) return true;
  const ts = new Date(value.replace(/-/g, '/')).getTime();
  if (start) {
    const startTs = new Date(`${start} 00:00`).getTime();
    if (ts < startTs) return false;
  }
  if (end) {
    const endTs = new Date(`${end} 23:59:59`).getTime();
    if (ts > endTs) return false;
  }
  return true;
};
