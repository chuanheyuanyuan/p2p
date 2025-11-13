import { Layout, Menu, Typography } from 'antd';
import type { MenuProps } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import { navSections } from '../constants/navigation';
import { hasRoleAccess } from '../constants/roles';
import { selectRoles, useAuthStore } from '../store/auth';

const { Sider } = Layout;

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const roles = useAuthStore(selectRoles);

  const matchKey = () => {
    const pathname = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '');
    const flatKeys = navSections.flatMap((section) => section.items.map((item) => item.key));
    return flatKeys.find((key) => pathname.startsWith(key)) ?? '/';
  };

  const filteredSections = useMemo(
    () =>
      navSections
        .map((section) => ({
          ...section,
          items: section.items.filter((item) => hasRoleAccess(roles, item.roles))
        }))
        .filter((section) => section.items.length > 0),
    [roles]
  );

  const menuItems: MenuProps['items'] = filteredSections.map((section) => ({
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
      {menuItems.length > 0 ? (
        <Menu
          mode="inline"
          selectedKeys={[matchKey()]}
          onClick={(info) => navigate(info.key)}
          items={menuItems}
        />
      ) : (
        <Typography.Text style={{ color: '#94a3b8' }}>当前角色暂无菜单，请联系管理员。</Typography.Text>
      )}
    </Sider>
  );
};

export default Sidebar;
