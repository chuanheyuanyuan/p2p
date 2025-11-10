import { Breadcrumb, Space, Tag, Typography } from 'antd';
import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { navKeyMap } from '../constants/navigation';

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

  const current = useMemo(() => {
    const path = location.pathname.replace(/\/$/, '') || '/';
    const matched = breadcrumbPatterns.find(({ pattern }) => pattern.test(path));
    if (matched) return matched.trail;
    return [navKeyMap.get(path) ?? ''];
  }, [location.pathname]);

  const breadcrumbItems = current
    .filter(Boolean)
    .map((title, index) => ({ key: `${title}-${index}`, title }));

  return (
    <div className="topbar">
      <Breadcrumb items={breadcrumbItems} />
      <Space size="large" align="center">
        <Typography.Text type="secondary">LT: 2025/10/20 08:13:52</Typography.Text>
        <Tag color="green">在线</Tag>
        <div className="avatar">OP</div>
      </Space>
    </div>
  );
};

export default Topbar;
