import { Routes, Route } from 'react-router-dom';
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

const App = () => (
  <Routes>
    <Route path="/" element={<AdminLayout />}>
      <Route index element={<Dashboard />} />
      <Route path="daily-stats" element={<DailyStats />} />
      <Route path="applications" element={<Applications />} />
      <Route path="applications/:id" element={<ApplicationDetail />} />
      <Route path="collections" element={<Collections />} />
      <Route path="case-detail" element={<CaseDetail />} />
      <Route path="users/:userId" element={<UserProfile />} />
      <Route path="ops" element={<OpsConfig />} />
      <Route path="app-upgrade" element={<AppUpgrade />} />
      <Route path="channel" element={<ChannelManagement />} />
    </Route>
  </Routes>
);

export default App;
