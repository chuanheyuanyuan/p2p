import { App as AntdApp, Breadcrumb, Dropdown, Space, Tag, Typography } from 'antd';
import { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { navKeyMap } from '../constants/navigation';
import { roleLabels } from '../constants/roles';
import { selectCurrentUser, selectRoles, useAuthStore } from '../store/auth';

const breadcrumbPatterns: Array<{ pattern: RegExp; trail: string[] }> = [
  { pattern: /^\/$/, trail: ['首页'] },
  { pattern: /^\/daily-stats\/?$/, trail: ['数据大盘'] },
  { pattern: /^\/applications\/?$/, trail: ['申请管理', '全部申请'] },
  { pattern: /^\/applications\/[^/]+$/, trail: ['申请管理', '申请详情'] },
  { pattern: /^\/collections\/?$/, trail: ['催收管理', '催收案件'] },
  { pattern: /^\/case-detail\/?$/, trail: ['催收管理', '案件详情'] },
  { pattern: /^\/users\/?$/, trail: ['用户管理', '用户档案'] },
  { pattern: /^\/users\/[^/]+$/, trail: ['用户管理', '用户档案'] },
  { pattern: /^\/ops\/?$/, trail: ['运营管理', '配置面板'] },
  { pattern: /^\/app-upgrade\/?$/, trail: ['运营管理', 'App 升级'] },
  { pattern: /^\/channel\/?$/, trail: ['运营管理', '渠道管理'] }
];

const Topbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const user = useAuthStore(selectCurrentUser);
  const roles = useAuthStore(selectRoles);
  const logout = useAuthStore((state) => state.logout);

  const current = useMemo(() => {
    const path = location.pathname.replace(/\/$/, '') || '/';
    const matched = breadcrumbPatterns.find(({ pattern }) => pattern.test(path));
    if (matched) return matched.trail;
    return [navKeyMap.get(path) ?? ''];
  }, [location.pathname]);

  const breadcrumbItems = current
    .filter(Boolean)
    .map((title, index) => ({ key: `${title}-${index}`, title }));

  const initials = user?.name
    ?.split(' ')
    .map((part) => part.charAt(0))
    .join('')
    .slice(0, 2)
    .toUpperCase() ?? 'OP';

  const menuItems = [
    {
      key: 'role',
      label: (
        <div>
          <div style={{ fontWeight: 600 }}>{user?.name ?? '未登录'}</div>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {user?.email ?? 'no-reply@inscash.com'}
          </Typography.Text>
        </div>
      ),
      disabled: true
    },
    { type: 'divider' as const },
    { key: 'logout', label: '退出登录' }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout();
      message.success('已退出登录');
      navigate('/login');
    }
  };

  const roleText = roles.map((role) => roleLabels[role]).join(' / ') || '未分配角色';

  return (
    <div className="topbar">
      <Breadcrumb items={breadcrumbItems} />
      <Space size="large" align="center">
        <Typography.Text type="secondary">{roleText}</Typography.Text>
        <Tag color="green">在线</Tag>
        <Dropdown menu={{ items: menuItems, onClick: handleMenuClick }}>
          <div className="avatar" role="button" aria-label="account menu">
            {initials}
          </div>
        </Dropdown>
      </Space>
    </div>
  );
};

export default Topbar;
