export interface DashboardKpi {
  label: string;
  value: string;
  delta: string;
}

export interface DailyStat {
  date: string;
  installs: number;
  regs: number;
  logins: number;
  applies: number;
  disburses: number;
  repayments: number;
  amount: number;
}

export interface ApplicationRecord {
  id: string;
  product: string;
  name: string;
  channel: string;
  level: string;
  amount: number;
  term: string;
  reviewer: string;
  status: '通过' | '拒绝';
}

export interface CollectionCase {
  caseId: string;
  user: string;
  bucket: string;
  amount: number;
  assignee: string;
  due: string;
  status: string;
}

export interface CaseDetailHistory {
  ts: string;
  text: string;
}

export interface CaseDetailProfile {
  name: string;
  gender: string;
  age: number;
  education: string;
  idType: string;
  idNo: string;
  address: string;
  married: string;
  gps: string;
}

export interface CaseDetailCustomer {
  loanNo: string;
  status: string;
  product: string;
  level: string;
  phone: string;
  sim: string;
  channel: string;
  authorize: string;
  device: string;
  submitAt: string;
}

export interface CaseDetail {
  customer: CaseDetailCustomer;
  profile: CaseDetailProfile;
  history: CaseDetailHistory[];
}

export interface OpsCard {
  title: string;
  description: string;
  action: string;
}

export interface ReleaseNote {
  version: string;
  date: string;
  highlight: string;
}

export const dashboardKpis: DashboardKpi[] = [
  { label: '今日放款金额', value: '₵93,800', delta: '+12.6% vs 昨日' },
  { label: '今日申请笔数', value: '27', delta: '首逾率 38.19%' },
  { label: '登录人数', value: '15', delta: '老客 14 · 新客 1' },
  { label: '催回金额', value: '₵0', delta: '今日已分配 0 单' }
];

export const dailyStatsMock: DailyStat[] = [
  { date: '2025-10-20', installs: 48, regs: 1, logins: 0, applies: 27, disburses: 15, repayments: 15, amount: 93800 },
  { date: '2025-10-19', installs: 197, regs: 7, logins: 7, applies: 110, disburses: 54, repayments: 25, amount: 20195 },
  { date: '2025-10-18', installs: 233, regs: 10, logins: 7, applies: 163, disburses: 109, repayments: 79, amount: 44296 },
  { date: '2025-10-17', installs: 256, regs: 11, logins: 12, applies: 197, disburses: 117, repayments: 117, amount: 45500 },
  { date: '2025-10-16', installs: 226, regs: 6, logins: 9, applies: 187, disburses: 121, repayments: 121, amount: 48090 }
];

export const applicationsMock: ApplicationRecord[] = [
  { id: '397709', product: 'InsCash Plus', name: 'Chiamaka Eddy-okafor', channel: 'Google Ads', level: 'Level5', amount: 150, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
  { id: '397708', product: 'InsCash Max', name: 'Nancy A. Osei', channel: 'Facebook Ads', level: 'Level5', amount: 550, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
  { id: '397706', product: 'InsCash Pro', name: 'Samuel Adu', channel: 'Facebook Ads', level: 'Level1', amount: 5000, term: '180D', reviewer: 'OCR 编辑', status: '拒绝' }
];

export const collectionCasesMock: CollectionCase[] = [
  { caseId: 'CASE-1001', user: 'Nancy Osei', bucket: 'D1', amount: 520, assignee: 'Team A', due: '2025-10-21', status: '工作中' },
  { caseId: 'CASE-1002', user: 'Samuel Adu', bucket: 'D7', amount: 1450, assignee: 'Team A', due: '2025-10-14', status: 'PTP 10/22' },
  { caseId: 'CASE-1003', user: 'Kobby Gomez', bucket: 'D15', amount: 2880, assignee: 'Team B', due: '2025-10-05', status: '转外包' }
];

export const caseDetailMock: CaseDetail = {
  customer: {
    loanNo: '397708',
    status: '还款期',
    product: 'InsCash Max',
    level: 'Level5',
    phone: '553****75',
    sim: 'HuZH6t+k3HuVOTHlHC3i5Q==',
    channel: 'Facebook Ads',
    authorize: '已授权',
    device: 'itel P671L',
    submitAt: '2025-10-20 08:06:08'
  },
  profile: {
    name: 'Nancy Agyapomaa Osei',
    gender: '女',
    age: 35,
    education: '大学',
    idType: '身份证',
    idNo: 'GHA-718571472-2',
    address: 'Ashanti Bantama BA 52',
    married: '未婚',
    gps: '6.6021, -1.6246'
  },
  history: [
    { ts: '2025-10-20 09:02', text: '案件创建，分配 Team A' },
    { ts: '2025-10-20 11:31', text: '坐席外呼：客户承诺 10/22 全额还款' },
    { ts: '2025-10-20 18:05', text: '发送催收短信' }
  ]
};

export const opsCardsMock: OpsCard[] = [
  { title: '账号与角色管理', description: '维护运营、催收、电销等后台权限，支持快速新增角色。', action: '进入配置' },
  { title: '产品与用户等级管理', description: '配置贷款产品、额度、费率与授信等级策略。', action: '编辑产品' },
  { title: '支付管理', description: '切换放款/还款通道，查看通道 SLA 与限额。', action: '查看通道' },
  { title: '申请审批配置', description: '维护机审/人审策略、阈值与队列。', action: '调整策略' },
  { title: '消息模板管理', description: '统一管理短信、Push、WhatsApp 模板与变量。', action: '管理模板' },
  { title: '渠道链接管理', description: '生成渠道落地页链接并对接 Kochava 归因。', action: '管理渠道' }
];

export const releasesMock: ReleaseNote[] = [
  { version: 'v1.0.17', date: '2025-10-15', highlight: '新增隐私合规弹窗、修复闪退。' },
  { version: 'v1.0.16', date: '2025-09-30', highlight: '优化注册链路，接入 Kochava。' },
  { version: 'v1.0.15', date: '2025-09-10', highlight: '上线新催收模板与语音策略。' }
];
