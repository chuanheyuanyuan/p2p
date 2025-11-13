import { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import type { AdminRole } from '../constants/roles';
import { hasRoleAccess } from '../constants/roles';
import { useAuthStore, selectAccessToken, selectRoles } from '../store/auth';

type PersistHelpers = {
  hasHydrated?: () => boolean;
  onFinishHydration?: (callback: () => void) => () => void;
  rehydrate?: () => Promise<void>;
};

const persistHelpers = (useAuthStore as typeof useAuthStore & { persist?: PersistHelpers }).persist;

const useAuthHydrated = () => {
  const [hydrated, setHydrated] = useState(persistHelpers?.hasHydrated?.() ?? true);

  useEffect(() => {
    if (!persistHelpers) return;
    const unsub = persistHelpers.onFinishHydration?.(() => setHydrated(true));
    if (!persistHelpers.hasHydrated?.()) {
      void persistHelpers.rehydrate?.();
    }
    return () => {
      unsub?.();
    };
  }, []);

  return hydrated;
};

export const RequireAuth = () => {
  const token = useAuthStore(selectAccessToken);
  const location = useLocation();
  const hydrated = useAuthHydrated();

  if (!hydrated) {
    return (
      <div className="page-centered">
        <Spin />
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

interface RoleGuardProps {
  allowedRoles?: AdminRole[];
  children: React.ReactNode;
}

export const RoleGuard = ({ allowedRoles, children }: RoleGuardProps) => {
  const roles = useAuthStore(selectRoles);

  if (!hasRoleAccess(roles, allowedRoles)) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
};
