import type { ReactNode } from 'react';
import {
  AppstoreOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  PartitionOutlined,
  SettingOutlined,
  TeamOutlined,
  UserSwitchOutlined
} from '@ant-design/icons';

export interface NavItem {
  key: string;
  label: string;
  icon?: ReactNode;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const navSections: NavSection[] = [
  {
    title: '核心',
    items: [
      { key: '/', label: '首页', icon: <DashboardOutlined /> },
      { key: '/daily-stats', label: '数据大盘', icon: <DatabaseOutlined /> },
      { key: '/applications', label: '申请管理', icon: <FileTextOutlined /> }
    ]
  },
  {
    title: '催收',
    items: [
      { key: '/collections', label: '催收案件', icon: <TeamOutlined /> },
      { key: '/case-detail', label: '案件详情', icon: <UserSwitchOutlined /> }
    ]
  },
  {
    title: '运营',
    items: [
      { key: '/ops', label: '运营配置', icon: <SettingOutlined /> },
      { key: '/app-upgrade', label: 'App 升级', icon: <AppstoreOutlined /> },
      { key: '/channel', label: '渠道管理', icon: <PartitionOutlined /> }
    ]
  }
];

export const navKeyMap = new Map(navSections.flatMap((section) => section.items.map((item) => [item.key, item.label])));
