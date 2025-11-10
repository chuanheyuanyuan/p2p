import { Breadcrumb, Space, Tag, Typography } from 'antd';
import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { navKeyMap } from '../constants/navigation';

const breadcrumbMap: Record<string, string[]> = {
  '/': ['首页'],
  '/daily-stats': ['数据大盘'],
  '/applications': ['申请管理', '全部申请'],
  '/collections': ['催收管理', '催收案件'],
  '/case-detail': ['催收管理', '案件详情'],
  '/ops': ['运营管理', '配置面板'],
  '/app-upgrade': ['运营管理', 'App 升级'],
  '/channel': ['运营管理', '渠道管理']
};

const Topbar = () => {
  const location = useLocation();

  const current = useMemo(() => {
    const path = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '');
    return breadcrumbMap[path] ?? [navKeyMap.get(path) ?? ''];
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
