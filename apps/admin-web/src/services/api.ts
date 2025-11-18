import { request } from './http';
import type {
  ApplicationDetail,
  ApplicationRecord,
  CollectionCase,
  CollectionCaseDetail,
  CollectionStats,
  DailyStat,
  DashboardStats,
  DisbursementRecord,
  ReconciliationRecord,
  RepaymentRecord,
  UserProfile
} from '../mocks/data';
import {
  applicationsMock,
  applicationDetailsMock,
  collectionCasesMock,
  collectionDetailsMock,
  collectionStatsMock,
  adminAccountsMock,
  dashboardMock,
  defaultSessionMock,
  dailyStatsMock,
  disbursementsMock,
  reconciliationsMock,
  repaymentsMock,
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
  caseId?: string;
  status?: string;
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

export interface CollectionActionPayload {
  action: string;
  result?: string;
  note?: string;
  status?: string;
  ptpAmount?: number;
  ptpDueAt?: string;
}

export async function createCollectionAction(caseId: string, payload: CollectionActionPayload): Promise<CollectionCaseDetail> {
  try {
    return await request(`/admin/v1/collections/cases/${caseId}/actions`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  } catch (error) {
    console.warn('createCollectionAction fallback', error);
    return fetchCollectionDetail(caseId);
  }
}

export async function fetchCollectionStats(): Promise<CollectionStats> {
  try {
    return await request('/admin/v1/collections/stats');
  } catch (error) {
    console.warn('fetchCollectionStats fallback', error);
    return collectionStatsMock;
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
  loanId?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
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

function buildSearchParams(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      search.append(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function fetchDisbursements(params: FinanceQuery): Promise<PaginatedResponse<DisbursementRecord>> {
  try {
    const query = buildSearchParams(params);
    return await request(`/admin/v1/finance/disbursements${query}`);
  } catch (error) {
    console.warn('fetchDisbursements fallback', error);
    return { list: disbursementsMock, total: disbursementsMock.length };
  }
}

export async function fetchRepayments(params: FinanceQuery): Promise<PaginatedResponse<RepaymentRecord>> {
  try {
    const query = buildSearchParams(params);
    return await request(`/admin/v1/finance/repayments${query}`);
  } catch (error) {
    console.warn('fetchRepayments fallback', error);
    return { list: repaymentsMock, total: repaymentsMock.length };
  }
}

export async function fetchReconciliations(params: { refType?: string; refId?: string; page?: number; pageSize?: number }): Promise<PaginatedResponse<ReconciliationRecord>> {
  try {
    const query = buildSearchParams(params);
    return await request(`/admin/v1/finance/reconciliations${query}`);
  } catch (error) {
    console.warn('fetchReconciliations fallback', error);
    return { list: reconciliationsMock, total: reconciliationsMock.length };
  }
}
