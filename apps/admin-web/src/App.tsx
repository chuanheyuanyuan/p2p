import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Dashboard from './pages/Dashboard';
import DailyStats from './pages/DailyStats';
import Applications from './pages/Applications';
import ApplicationDetail from './pages/ApplicationDetail';
import Collections from './pages/Collections';
import CaseDetail from './pages/CaseDetail';
import OpsConfig from './pages/OpsConfig';
import AppUpgrade from './pages/AppUpgrade';
import ChannelManagement from './pages/ChannelManagement';
import UserProfile from './pages/UserProfile';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';
import { RequireAuth, RoleGuard } from './components/RouteGuards';
import { routeRoleMap } from './constants/navigation';

const App = () => (
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route element={<RequireAuth />}>
      <Route path="/" element={<AdminLayout />}>
        <Route
          index
          element={
            <RoleGuard allowedRoles={routeRoleMap['/']}>
              <Dashboard />
            </RoleGuard>
          }
        />
        <Route
          path="daily-stats"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/daily-stats']}>
              <DailyStats />
            </RoleGuard>
          }
        />
        <Route
          path="applications"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/applications']}>
              <Applications />
            </RoleGuard>
          }
        />
        <Route
          path="applications/:id"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/applications/:id']}>
              <ApplicationDetail />
            </RoleGuard>
          }
        />
        <Route
          path="collections"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/collections']}>
              <Collections />
            </RoleGuard>
          }
        />
        <Route
          path="case-detail"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/case-detail']}>
              <CaseDetail />
            </RoleGuard>
          }
        />
        <Route
          path="users/:userId"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/users/:userId']}>
              <UserProfile />
            </RoleGuard>
          }
        />
        <Route
          path="ops"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/ops']}>
              <OpsConfig />
            </RoleGuard>
          }
        />
        <Route
          path="app-upgrade"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/app-upgrade']}>
              <AppUpgrade />
            </RoleGuard>
          }
        />
        <Route
          path="channel"
          element={
            <RoleGuard allowedRoles={routeRoleMap['/channel']}>
              <ChannelManagement />
            </RoleGuard>
          }
        />
        <Route path="403" element={<Unauthorized />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;
