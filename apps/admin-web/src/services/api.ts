import { request } from './http';
import type {
  ApplicationDetail,
  ApplicationRecord,
  CollectionCase,
  CollectionCaseDetail,
  DailyStat,
  DashboardStats,
  OpsProductConfig,
  GradeConfig,
  ChannelLinkConfig,
  MessageTemplateConfig,
  ApprovalRuleConfig,
  ReleaseNote,
  UserProfile,
  ReportCenterData
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
  opsProductsMock,
  gradeConfigsMock,
  channelLinksMock,
  messageTemplatesMock,
  approvalRulesMock,
  releasesMock,
  userProfilesMock,
  reportCenterMock
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

export interface ReportCenterQuery {
  businessDate: string;
  channel?: string;
  product?: string;
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

export async function fetchReportCenter(params: ReportCenterQuery): Promise<ReportCenterData> {
  try {
    const search = new URLSearchParams();
    search.append('businessDate', params.businessDate);
    if (params.channel && params.channel !== 'all') {
      search.append('channel', params.channel);
    }
    if (params.product && params.product !== 'all') {
      search.append('product', params.product);
    }
    const query = search.toString();
    const endpoint = query ? `/admin/v1/reports/center?${query}` : '/admin/v1/reports/center';
    return await request<ReportCenterData>(endpoint);
  } catch (error) {
    console.warn('fetchReportCenter fallback', error);
    return {
      ...reportCenterMock,
      filters: {
        businessDate: params.businessDate,
        channel: params.channel ?? null,
        product: params.product ?? null
      }
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

export async function fetchOpsProducts(): Promise<OpsProductConfig[]> {
  try {
    return await request('/admin/v1/ops/products');
  } catch (error) {
    console.warn('fetchOpsProducts fallback', error);
    return opsProductsMock;
  }
}

export async function fetchGradeConfigs(): Promise<GradeConfig[]> {
  try {
    return await request('/admin/v1/ops/grades');
  } catch (error) {
    console.warn('fetchGradeConfigs fallback', error);
    return gradeConfigsMock;
  }
}

export async function fetchChannelLinks(): Promise<ChannelLinkConfig[]> {
  try {
    return await request('/admin/v1/channel/links');
  } catch (error) {
    console.warn('fetchChannelLinks fallback', error);
    return channelLinksMock;
  }
}

export async function fetchMessageTemplates(): Promise<MessageTemplateConfig[]> {
  try {
    return await request('/admin/v1/ops/messages');
  } catch (error) {
    console.warn('fetchMessageTemplates fallback', error);
    return messageTemplatesMock;
  }
}

export async function fetchApprovalRules(): Promise<ApprovalRuleConfig[]> {
  try {
    return await request('/admin/v1/ops/approval-rules');
  } catch (error) {
    console.warn('fetchApprovalRules fallback', error);
    return approvalRulesMock;
  }
}

export async function fetchAppReleases(): Promise<ReleaseNote[]> {
  try {
    return await request('/admin/v1/ops/releases');
  } catch (error) {
    console.warn('fetchAppReleases fallback', error);
    return releasesMock;
  }
}
