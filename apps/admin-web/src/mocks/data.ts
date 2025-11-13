export interface DashboardKpi {
  label: string;
  value: string;
  delta: string;
}

export interface DashboardStats {
  kpis: DashboardKpi[];
  overdue: {
    rate: number;
    dueToday: number;
    repaid: number;
    yesterdayRate: number;
    progress: number;
  };
  recovery: {
    cases: number;
    assigned: number;
    note: string;
  };
  today: {
    installs: number;
    regs: number;
    logins: number;
    applies: number;
    disburses: number;
    repayments: number;
  };
  conversion: {
    percent: number;
    numerator: number;
    denominator: number;
  };
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
  userId: string;
  product: string;
  name: string;
  channel: string;
  level: string;
  amount: number;
  term: string;
  reviewer: string;
  status: '通过' | '拒绝';
}

export interface ApprovalNode {
  node: string;
  result: string;
  operator: string;
  remark?: string;
  time: string;
}

export interface ApplicationHistoryEntry {
  ts: string;
  event: string;
  actor: string;
}

export interface ApplicationDetail {
  application: ApplicationRecord;
  basic: {
    applyTime: string;
    productVersion: string;
    deviceBrand: string;
    deviceModel: string;
    appVersion: string;
    source: string;
    repeated: boolean;
  };
  approval: ApprovalNode[];
  history: ApplicationHistoryEntry[];
}

export interface CollectionCase {
  caseId: string;
  user: string;
  bucket: string;
  amount: number;
  principalDue: number;
  overdueDays: number;
  ptpStatus: string;
  assignee: string;
  channel: string;
  due: string;
  status: string;
}

export interface CollectionFollowUp {
  ts: string;
  actor: string;
  action: string;
  result: string;
}

export interface CollectionPTPRecord {
  ts: string;
  amount: number;
  promiseDate: string;
  status: '有效' | '失效';
  note?: string;
}

export interface CollectionCallLog {
  ts: string;
  channel: string;
  duration: string;
  note: string;
}

export interface CollectionContactInfo {
  phone: string;
  altPhone?: string;
  whatsapp?: string;
  address: string;
}

export interface CollectionCaseDetail {
  summary: {
    caseId: string;
    user: string;
    bucket: string;
    overdueDays: number;
    amount: number;
    ptpStatus: string;
    device: string;
  };
  contact: CollectionContactInfo;
  followUps: CollectionFollowUp[];
  ptpRecords: CollectionPTPRecord[];
  callLogs: CollectionCallLog[];
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

export interface UserProfile {
  userId: string;
  name: string;
  gender: string;
  phone: string;
  email: string;
  level: string;
  kycStatus: string;
  registerDate: string;
  lastLogin: string;
  tags: string[];
  riskFlags: string[];
  address: string;
  gps: string;
  blacklisted: boolean;
}

export interface AdminAccount {
  id: string;
  username: string;
  password: string;
  name: string;
  email: string;
  roles: AdminRole[];
  permissions: string[];
  title?: string;
}

export const dashboardKpis: DashboardKpi[] = [
  { label: '今日放款金额', value: '₵93,800', delta: '+12.6% vs 昨日' },
  { label: '今日申请笔数', value: '27', delta: '首逾率 38.19%' },
  { label: '登录人数', value: '15', delta: '老客 14 · 新客 1' },
  { label: '催回金额', value: '₵0', delta: '今日已分配 0 单' }
];

export const dashboardMock: DashboardStats = {
  kpis: dashboardKpis,
  overdue: {
    rate: 38.19,
    dueToday: 166,
    repaid: 18,
    yesterdayRate: 45.61,
    progress: 65
  },
  recovery: {
    cases: 0,
    assigned: 0,
    note: '今日已分配 0 · 催收团队待命'
  },
  today: {
    installs: 48,
    regs: 1,
    logins: 15,
    applies: 27,
    disburses: 15,
    repayments: 15
  },
  conversion: {
    percent: 12,
    numerator: 27,
    denominator: 220
  }
};

export const dailyStatsMock: DailyStat[] = [
  { date: '2025-10-20', installs: 48, regs: 1, logins: 0, applies: 27, disburses: 15, repayments: 15, amount: 93800 },
  { date: '2025-10-19', installs: 197, regs: 7, logins: 7, applies: 110, disburses: 54, repayments: 25, amount: 20195 },
  { date: '2025-10-18', installs: 233, regs: 10, logins: 7, applies: 163, disburses: 109, repayments: 79, amount: 44296 },
  { date: '2025-10-17', installs: 256, regs: 11, logins: 12, applies: 197, disburses: 117, repayments: 117, amount: 45500 },
  { date: '2025-10-16', installs: 226, regs: 6, logins: 9, applies: 187, disburses: 121, repayments: 121, amount: 48090 }
];

export const adminAccountsMock: AdminAccount[] = [
  {
    id: 'staff-ops-01',
    username: 'ops.lead',
    password: 'admin123',
    name: 'Ama Boateng',
    email: 'ops.lead@inscash.com',
    roles: ['super_admin', 'ops_manager', 'analyst', 'channel_ops'],
    permissions: ['applications:read', 'ops:write', 'reports:view', 'channel:manage'],
    title: '运营负责人'
  },
  {
    id: 'staff-collector-07',
    username: 'collector.jr',
    password: 'collector123',
    name: 'Yaw Mensah',
    email: 'collector.jr@inscash.com',
    roles: ['collector_agent'],
    permissions: ['collections:workbench'],
    title: 'D1 坐席'
  },
  {
    id: 'staff-analyst-03',
    username: 'analyst',
    password: 'analyst123',
    name: 'Efua Owusu',
    email: 'analyst@inscash.com',
    roles: ['analyst'],
    permissions: ['reports:view'],
    title: '数据分析师'
  }
];

export const defaultSessionMock: LoginResponse = {
  accessToken: 'mock-admin-token',
  refreshToken: 'mock-refresh-token',
  expiresIn: 3600,
  user: {
    id: 'staff-ops-01',
    name: 'Ama Boateng',
    email: 'ops.lead@inscash.com',
    title: '运营负责人'
  },
  roles: ['super_admin', 'ops_manager', 'analyst', 'channel_ops'],
  permissions: ['applications:read', 'ops:write', 'reports:view', 'channel:manage']
};

export const applicationsMock: ApplicationRecord[] = [
  { id: '397709', userId: 'U10001', product: 'InsCash Plus', name: 'Chiamaka Eddy-okafor', channel: 'Google Ads', level: 'Level5', amount: 150, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
  { id: '397708', userId: 'U10002', product: 'InsCash Max', name: 'Nancy A. Osei', channel: 'Facebook Ads', level: 'Level5', amount: 550, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
  { id: '397706', userId: 'U10003', product: 'InsCash Pro', name: 'Samuel Adu', channel: 'Facebook Ads', level: 'Level1', amount: 5000, term: '180D', reviewer: 'OCR 编辑', status: '拒绝' }
];

export const collectionCasesMock: CollectionCase[] = [
  {
    caseId: 'CASE-1001',
    user: 'Nancy Osei',
    bucket: 'D1',
    amount: 520,
    principalDue: 480,
    overdueDays: 1,
    ptpStatus: 'PTP 10/22',
    assignee: 'Team A / Sitsofe',
    channel: 'Facebook Ads',
    due: '2025-10-21',
    status: '工作中'
  },
  {
    caseId: 'CASE-1002',
    user: 'Samuel Adu',
    bucket: 'D7',
    amount: 1450,
    principalDue: 1300,
    overdueDays: 7,
    ptpStatus: '未承诺',
    assignee: 'Team A / Sitsofe',
    channel: 'Facebook Ads',
    due: '2025-10-14',
    status: 'PTP 10/22'
  },
  {
    caseId: 'CASE-1003',
    user: 'Kobby Gomez',
    bucket: 'D15',
    amount: 2880,
    principalDue: 2500,
    overdueDays: 15,
    ptpStatus: '转外包',
    assignee: 'Team B / Dora',
    channel: 'Google Ads',
    due: '2025-10-05',
    status: '转外包'
  }
];

export const collectionDetailsMock: Record<string, CollectionCaseDetail> = {
  'CASE-1001': {
    summary: {
      caseId: 'CASE-1001',
      user: 'Nancy Osei',
      bucket: 'D1',
      overdueDays: 1,
      amount: 520,
      ptpStatus: 'PTP 10/22',
      device: 'Android · Itel P671L'
    },
    contact: {
      phone: '+233-553-000-175',
      whatsapp: '+233-553-000-175',
      address: 'Ashanti Bantama BA 52'
    },
    followUps: [
      { ts: '2025-10-20 11:31', actor: 'Sitsofe', action: '外呼', result: '客户承诺 10/22 全额' },
      { ts: '2025-10-20 09:15', actor: '系统', action: '短信', result: '发送催收短信模板 L1' }
    ],
    ptpRecords: [
      { ts: '2025-10-20 11:31', amount: 520, promiseDate: '2025-10-22', status: '有效', note: '客户表示薪水到账即还' }
    ],
    callLogs: [
      { ts: '2025-10-20 11:31', channel: '外呼', duration: '03:15', note: '语气平稳，确认 10/22 还款' },
      { ts: '2025-10-20 10:02', channel: '外呼', duration: '00:35', note: '无人接听' }
    ]
  },
  'CASE-1002': {
    summary: {
      caseId: 'CASE-1002',
      user: 'Samuel Adu',
      bucket: 'D7',
      overdueDays: 7,
      amount: 1450,
      ptpStatus: '未承诺',
      device: 'Android · Samsung A21'
    },
    contact: {
      phone: '+233-553-888-002',
      altPhone: '+233-550-888-200',
      address: 'Kumasi, Ghana'
    },
    followUps: [
      { ts: '2025-10-20 16:45', actor: 'Sitsofe', action: '外呼', result: '拒接' },
      { ts: '2025-10-19 10:20', actor: '系统', action: '短信', result: '发送 D7 模板' }
    ],
    ptpRecords: [],
    callLogs: [
      { ts: '2025-10-20 16:45', channel: '外呼', duration: '00:05', note: '拒接' },
      { ts: '2025-10-18 15:10', channel: 'WhatsApp', duration: '文本', note: '提醒付款' }
    ]
  },
  'CASE-1003': {
    summary: {
      caseId: 'CASE-1003',
      user: 'Kobby Gomez',
      bucket: 'D15',
      overdueDays: 15,
      amount: 2880,
      ptpStatus: '转外包',
      device: 'Android · Tecno Spark'
    },
    contact: {
      phone: '+233-551-123-444',
      address: 'Accra, Ghana'
    },
    followUps: [
      { ts: '2025-10-18 08:05', actor: 'Dora', action: '外呼', result: '无人接听' },
      { ts: '2025-10-17 12:00', actor: '系统', action: '推送', result: '通知已送达' }
    ],
    ptpRecords: [
      { ts: '2025-10-10 09:00', amount: 1000, promiseDate: '2025-10-12', status: '失效', note: '未按时付款' }
    ],
    callLogs: [
      { ts: '2025-10-18 08:05', channel: '外呼', duration: '00:10', note: '无人接听' }
    ]
  }
};

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

export const applicationDetailsMock: Record<string, ApplicationDetail> = Object.fromEntries(
  applicationsMock.map((application) => [
    application.id,
    {
      application,
      basic: {
        applyTime: '2025-10-20 08:06:08',
        productVersion: '2025Q4',
        deviceBrand: 'Itel',
        deviceModel: 'itel P671L',
        appVersion: '1.0.17',
        source: application.channel,
        repeated: application.id === '397708'
      },
      approval: [
        { node: '机审', result: application.status === '通过' ? '通过' : '拒绝', operator: '规则引擎', time: '2025-10-20 08:06:30' },
        { node: '人工复核', result: application.status, operator: '审批员 A', remark: 'OCR 编辑', time: '2025-10-20 08:08:10' }
      ],
      history: [
        { ts: '2025-10-19 21:10', event: '提交申请', actor: application.name },
        { ts: '2025-10-20 08:06', event: '机审完成', actor: '风控系统' },
        { ts: '2025-10-20 08:08', event: '人工审批', actor: '审批员 A' }
      ]
    }
  ])
);

export const userProfilesMock: Record<string, UserProfile> = {
  U10001: {
    userId: 'U10001',
    name: 'Chiamaka Eddy-okafor',
    gender: '女',
    phone: '+233-553-001-123',
    email: 'chiamaka@example.com',
    level: 'Level5',
    kycStatus: '已通过',
    registerDate: '2024-11-20',
    lastLogin: '2025-10-20 07:55',
    tags: ['复借', '高价值'],
    riskFlags: ['设备可信'],
    address: 'Accra, Ghana',
    gps: '5.6037, -0.1870',
    blacklisted: false
  },
  U10002: {
    userId: 'U10002',
    name: 'Nancy Agyapomaa Osei',
    gender: '女',
    phone: '+233-553-000-175',
    email: 'nancy.osei@example.com',
    level: 'Level5',
    kycStatus: '已通过',
    registerDate: '2024-09-10',
    lastLogin: '2025-10-20 08:03',
    tags: ['社交渠道'],
    riskFlags: ['通讯录稀疏'],
    address: 'Ashanti Bantama BA 52',
    gps: '6.6021, -1.6246',
    blacklisted: false
  },
  U10003: {
    userId: 'U10003',
    name: 'Samuel Asiedu Adu',
    gender: '男',
    phone: '+233-553-888-002',
    email: 'samuel.adu@example.com',
    level: 'Level1',
    kycStatus: '待审核',
    registerDate: '2025-01-05',
    lastLogin: '2025-10-19 21:30',
    tags: ['新客'],
    riskFlags: ['设备更换频繁'],
    address: 'Kumasi, Ghana',
    gps: '6.6906, -1.6209',
    blacklisted: false
  }
};
import type { AdminRole } from '../constants/roles';
import type { LoginResponse } from '../types/auth';
