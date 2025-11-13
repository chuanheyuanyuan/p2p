import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AdminRole } from '../constants/roles';
import type { AdminUser, AuthSession } from '../types/auth';

interface AuthStoreShape {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  user: AdminUser | null;
  roles: AdminRole[];
  permissions: string[];
}

interface AuthState extends AuthStoreShape {
  setSession: (session: AuthSession) => void;
  logout: () => void;
}

const initialState: AuthStoreShape = {
  accessToken: null,
  refreshToken: null,
  expiresAt: null,
  user: null,
  roles: [],
  permissions: []
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      ...initialState,
      setSession: (session: AuthSession) =>
        set({
          accessToken: session.accessToken,
          refreshToken: session.refreshToken ?? null,
          expiresAt: session.expiresIn ? Date.now() + session.expiresIn * 1000 : null,
          user: session.user,
          roles: session.roles,
          permissions: session.permissions
        }),
      logout: () => set(initialState)
    }),
    {
      name: 'admin-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        expiresAt: state.expiresAt,
        user: state.user,
        roles: state.roles,
        permissions: state.permissions
      })
    }
  )
);

export const selectAccessToken = (state: AuthState) => state.accessToken;
export const selectRoles = (state: AuthState) => state.roles;
export const selectCurrentUser = (state: AuthState) => state.user;
