import { Layout, Menu, Typography } from 'antd';
import type { MenuProps } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { navSections } from '../constants/navigation';

const { Sider } = Layout;

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const matchKey = () => {
    const pathname = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '');
    const flatKeys = navSections.flatMap((section) => section.items.map((item) => item.key));
    return flatKeys.find((key) => pathname.startsWith(key)) ?? '/';
  };

  const menuItems: MenuProps['items'] = navSections.map((section) => ({
    type: 'group',
    label: <span className="menu-section-label">{section.title}</span>,
    key: section.title,
    children: section.items.map((item) => ({
      key: item.key,
      icon: item.icon,
      label: item.label
    }))
  }));

  return (
    <Sider width={230} className="app-sidebar">
      <div className="sidebar-brand">
        <Typography.Title level={4}>InsCash</Typography.Title>
        <Typography.Text>运营管理</Typography.Text>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[matchKey()]}
        onClick={(info) => navigate(info.key)}
        items={menuItems}
      />
    </Sider>
  );
};

export default Sidebar;
