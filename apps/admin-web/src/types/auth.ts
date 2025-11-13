import type { AdminRole } from '../constants/roles';

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  title?: string;
  avatar?: string;
}

export interface AuthSession {
  accessToken: string;
  refreshToken?: string;
  expiresIn?: number;
  user: AdminUser;
  roles: AdminRole[];
  permissions: string[];
}

export interface LoginPayload {
  username: string;
  password: string;
  otpCode?: string;
}

export interface LoginResponse extends AuthSession {}
