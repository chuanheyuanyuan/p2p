import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

const { Content } = Layout;

const AdminLayout = () => (
  <Layout className="admin-layout">
    <Sidebar />
    <Layout>
      <Topbar />
      <Content className="content-wrapper">
        <Outlet />
      </Content>
    </Layout>
  </Layout>
);

export default AdminLayout;
