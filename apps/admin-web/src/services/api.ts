import { request } from './http';
import type {
  ApplicationDetail,
  ApplicationRecord,
  CollectionCase,
  CollectionCaseDetail,
  DailyStat,
  UserProfile
} from '../mocks/data';
import {
  applicationsMock,
  applicationDetailsMock,
  collectionCasesMock,
  collectionDetailsMock,
  dailyStatsMock,
  userProfilesMock
} from '../mocks/data';

interface PaginatedResponse<T> {
  list: T[];
  total: number;
}

export interface ApplicationQuery {
  page?: number;
  pageSize?: number;
  keyword?: string;
  product?: string;
  level?: string;
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
