export type AdminRole =
  | 'super_admin'
  | 'loan_officer'
  | 'risk_officer'
  | 'finance'
  | 'collector_manager'
  | 'collector_agent'
  | 'ops_manager'
  | 'channel_ops'
  | 'analyst';

export const roleLabels: Record<AdminRole, string> = {
  super_admin: '超级管理员',
  loan_officer: '审批员',
  risk_officer: '风控运营',
  finance: '财务',
  collector_manager: '催收主管',
  collector_agent: '催收坐席',
  ops_manager: '运营配置',
  channel_ops: '渠道运营',
  analyst: '数据分析'
};

export const hasRoleAccess = (userRoles: AdminRole[], allowed?: AdminRole[]) => {
  if (!allowed || allowed.length === 0) return true;
  return userRoles.some((role) => allowed.includes(role));
};

export const allRoles: AdminRole[] = [
  'super_admin',
  'loan_officer',
  'risk_officer',
  'finance',
  'collector_manager',
  'collector_agent',
  'ops_manager',
  'channel_ops',
  'analyst'
];
