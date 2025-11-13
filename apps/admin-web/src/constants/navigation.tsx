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
import type { AdminRole } from './roles';
import { allRoles } from './roles';

export interface NavItem {
  key: string;
  label: string;
  icon?: ReactNode;
  roles: AdminRole[];
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

const approvalRoles: AdminRole[] = ['super_admin', 'loan_officer', 'risk_officer', 'ops_manager'];
const analyticsRoles: AdminRole[] = ['super_admin', 'analyst', 'ops_manager'];
const collectionsRoles: AdminRole[] = ['super_admin', 'collector_manager', 'collector_agent'];
const opsRoles: AdminRole[] = ['super_admin', 'ops_manager'];
const channelRoles: AdminRole[] = ['super_admin', 'channel_ops', 'ops_manager'];

export const navSections: NavSection[] = [
  {
    title: '核心',
    items: [
      { key: '/', label: '首页', icon: <DashboardOutlined />, roles: allRoles },
      { key: '/daily-stats', label: '数据大盘', icon: <DatabaseOutlined />, roles: analyticsRoles },
      { key: '/applications', label: '申请管理', icon: <FileTextOutlined />, roles: approvalRoles }
    ]
  },
  {
    title: '催收',
    items: [
      { key: '/collections', label: '催收案件', icon: <TeamOutlined />, roles: collectionsRoles },
      { key: '/case-detail', label: '案件详情', icon: <UserSwitchOutlined />, roles: collectionsRoles }
    ]
  },
  {
    title: '运营',
    items: [
      { key: '/ops', label: '运营配置', icon: <SettingOutlined />, roles: opsRoles },
      { key: '/app-upgrade', label: 'App 升级', icon: <AppstoreOutlined />, roles: opsRoles },
      { key: '/channel', label: '渠道管理', icon: <PartitionOutlined />, roles: channelRoles }
    ]
  }
];

export const navKeyMap = new Map(navSections.flatMap((section) => section.items.map((item) => [item.key, item.label])));

export const routeRoleMap: Record<string, AdminRole[]> = {
  '/': allRoles,
  '/daily-stats': analyticsRoles,
  '/applications': approvalRoles,
  '/applications/:id': approvalRoles,
  '/users/:userId': ['super_admin', 'loan_officer', 'risk_officer', 'collector_manager'],
  '/collections': collectionsRoles,
  '/case-detail': collectionsRoles,
  '/ops': opsRoles,
  '/app-upgrade': opsRoles,
  '/channel': channelRoles
};
