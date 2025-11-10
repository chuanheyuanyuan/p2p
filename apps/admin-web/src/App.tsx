import { Routes, Route } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Dashboard from './pages/Dashboard';
import DailyStats from './pages/DailyStats';
import Applications from './pages/Applications';
import Collections from './pages/Collections';
import CaseDetail from './pages/CaseDetail';
import OpsConfig from './pages/OpsConfig';
import AppUpgrade from './pages/AppUpgrade';
import ChannelManagement from './pages/ChannelManagement';

const App = () => (
  <Routes>
    <Route path="/" element={<AdminLayout />}>
      <Route index element={<Dashboard />} />
      <Route path="daily-stats" element={<DailyStats />} />
      <Route path="applications" element={<Applications />} />
      <Route path="collections" element={<Collections />} />
      <Route path="case-detail" element={<CaseDetail />} />
      <Route path="ops" element={<OpsConfig />} />
      <Route path="app-upgrade" element={<AppUpgrade />} />
      <Route path="channel" element={<ChannelManagement />} />
    </Route>
  </Routes>
);

export default App;
