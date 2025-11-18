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

export interface ReportSummaryItem {
  label: string;
  value: string;
  delta: number;
  description?: string;
}

export interface OverdueMigrationRow {
  stage: string;
  todayRate: number;
  yesterdayRate: number;
  change: number;
  note?: string;
}

export interface ChannelFunnelRow {
  channel: string;
  installs: number;
  regs: number;
  applies: number;
  disburses: number;
  conversion: number;
}

export interface ReborrowRateRow {
  segment: string;
  rate: number;
  change: number;
  volume: number;
}

export interface ReportCenterData {
  summary: ReportSummaryItem[];
  overdueMigration: OverdueMigrationRow[];
  channelFunnel: ChannelFunnelRow[];
  reborrowRates: ReborrowRateRow[];
  filters: {
    businessDate: string;
    channel?: string | null;
    product?: string | null;
  };
  lastUpdated: string;
  notes: string[];
}

export interface ApplicationRecord {
  id: string;
  userId: string;
  product: string;
  name: string;
  phone: string;
  channel: string;
  level: string;
  amount: number;
  term: string;
  reviewer: string;
  status: '通过' | '拒绝' | '审核中' | '待签署';
  statusCode?: string;
  submittedAt: string;
  appVersion: string;
  tags?: string[];
  repeat?: boolean;
  riskScore?: number;
  autoDecision?: string;
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

export interface ApplicationDocument {
  type: string;
  name: string;
  url: string;
  updatedAt: string;
}

export interface ApplicationDetail {
  application: ApplicationRecord;
  basic: {
    applyTime: string;
    productVersion: string;
    deviceBrand: string;
    deviceModel: string;
    appVersion: string;
    platform: string;
    source: string;
  };
  customer: {
    sim: string;
    email: string;
    gender: string;
    age: number;
    idType: string;
    idNumber: string;
    education: string;
    maritalStatus: string;
    address: string;
    gps: string;
  };
  approval: ApprovalNode[];
  approvalSummary: {
    autoDecision: string;
    manualDecision: string;
    riskScore: number;
    reasons: string[];
  };
  history: ApplicationHistoryEntry[];
  documents: ApplicationDocument[];
}

export interface CollectionCase {
  caseId: string;
  user: string;
  bucket: string;
  amount: number;
  principalDue: number;
  overdueDays: number;
  ptpStatus?: string;
  assignee?: string;
  channel?: string;
  due?: string;
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
  phone?: string;
  altPhone?: string;
  whatsapp?: string;
  address?: string;
}

export interface CollectionCaseDetail {
  summary: {
    caseId: string;
    user: string;
    bucket: string;
    overdueDays: number;
    amount: number;
    ptpStatus?: string;
    device?: string;
    principalDue?: number;
    assignee?: string;
    channel?: string;
    due?: string;
    status?: string;
  };
  contact: CollectionContactInfo;
  followUps: CollectionFollowUp[];
  ptpRecords: CollectionPTPRecord[];
  ptpDueAt?: string;
  ptpAmount?: number;
  callLogs?: CollectionCallLog[];
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

export interface BorrowerLoanSummary {
  totalLoans: number;
  activeLoans: number;
  outstandingAmount?: number;
  lastLoanId?: string;
  lastStatus?: string;
  lastSubmittedAt?: string;
  repeat?: boolean;
}

export interface BorrowerDeviceInfo {
  deviceId?: string;
  platform?: string;
  appVersion?: string;
  lastActiveAt?: string;
  privacyConsent?: boolean;
  locationConsent?: boolean;
}

export interface BorrowerKycInfo {
  status: string;
  docType?: string;
  docNumber?: string;
  reviewer?: string;
  reviewedAt?: string;
}

export interface BorrowerCollectionSummary {
  openCases: number;
  lastBucket?: string;
  lastStatus?: string;
  lastActionAt?: string;
}

export interface DisbursementRecord {
  reqNo: string;
  loanId: string;
  amount: number;
  channel: string;
  status: string;
  failureReason?: string;
  createdAt: string;
  updatedAt: string;
  account: Record<string, unknown>;
}

export interface RepaymentRecord {
  repaymentId: string;
  loanId: string;
  amount: number;
  currency: string;
  channel: string;
  status: string;
  txnRef: string;
  appliedAmount: number;
  remainingDue: number;
  paidAt: string;
  createdAt: string;
}

export interface ReconciliationRecord {
  entryId: string;
  refType: string;
  refId: string;
  status: string;
  lineCount: number;
  createdAt: string;
}

export interface UserProfile {
  userId: string;
  name: string;
  gender?: string;
  phone?: string;
  email?: string;
  level: string;
  kycStatus: string;
  registerDate?: string;
  lastLogin?: string;
  tags: string[];
  riskFlags: string[];
  address?: string;
  gps?: string;
  blacklisted: boolean;
  loanSummary?: BorrowerLoanSummary;
  device?: BorrowerDeviceInfo;
  kyc?: BorrowerKycInfo;
  collectionSummary?: BorrowerCollectionSummary;
}

export interface FinanceDisbursement {
  id: string;
  loanId: string;
  user: string;
  amount: number;
  channel: string;
  status: '待打款' | '成功' | '失败' | '重试中';
  currency: string;
  requestedAt: string;
  updatedAt: string;
  failureReason?: string;
  attempts: number;
  ledgerEntryId?: string;
}

export interface FinanceRepayment {
  repaymentId: string;
  loanId: string;
  user: string;
  amount: number;
  channel: string;
  status: '待入账' | '成功' | '失败' | '异常';
  currency: string;
  paidAt: string;
  recordedAt: string;
  method: string;
  ledgerEntryId?: string;
  difference?: number;
}

export interface ReconciliationDiff {
  id: string;
  date: string;
  type: '放款' | '还款';
  channel: string;
  channelAmount: number;
  ledgerAmount: number;
  currency: string;
  status: '未处理' | '处理中' | '已解决';
  note?: string;
}

export interface OpsProductConfig {
  productId: string;
  name: string;
  minAmount: number;
  maxAmount: number;
  termOptions: string;
  apr: number;
  allowExtension: boolean;
  status: '启用' | '停用';
}

export interface GradeConfig {
  grade: string;
  maxCredit: number;
  interestDiscount: number;
  autoUpgradeDays: number;
  rules: string[];
}

export interface ChannelLinkConfig {
  id: string;
  name: string;
  channel: string;
  status: '上线' | '停用';
  conversion: number;
  budget: number;
  updatedAt: string;
}

export interface MessageTemplateConfig {
  id: string;
  name: string;
  channel: 'SMS' | 'WhatsApp' | 'Push';
  active: boolean;
  preview: string;
  variables: string[];
}

export interface ApprovalRuleConfig {
  id: string;
  name: string;
  stage: '机审' | '人审';
  condition: string;
  action: string;
  owner: string;
  updatedAt: string;
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
  },
  {
    id: 'staff-finance-01',
    username: 'finance.lead',
    password: 'finance123',
    name: 'Abena Owusu Afriyie',
    email: 'finance.lead@inscash.com',
    roles: ['finance'],
    permissions: ['finance:read', 'finance:retry'],
    title: '财务负责人'
  },
  {
    id: 'staff-super-00',
    username: 'super.admin',
    password: 'super123',
    name: 'Kwesi Mensah',
    email: 'super.admin@inscash.com',
    roles: [
      'super_admin',
      'loan_officer',
      'risk_officer',
      'finance',
      'collector_manager',
      'collector_agent',
      'ops_manager',
      'channel_ops',
      'analyst'
    ],
    permissions: ['*'],
    title: '超级管理员'
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
  roles: ['super_admin', 'finance', 'ops_manager', 'analyst', 'channel_ops'],
  permissions: ['applications:read', 'ops:write', 'reports:view', 'channel:manage', 'finance:read']
};

export const financeDisbursementsMock: FinanceDisbursement[] = [
  {
    id: 'DISB-20251020001',
    loanId: 'LN202510200001',
    user: 'Chiamaka Eddy-okafor',
    amount: 150,
    currency: 'GHS',
    channel: 'Bank Transfer',
    status: '成功',
    requestedAt: '2025-10-20 08:07',
    updatedAt: '2025-10-20 08:12',
    attempts: 1,
    ledgerEntryId: 'LEDGER-9001'
  },
  {
    id: 'DISB-20251020018',
    loanId: 'LN202510190031',
    user: 'Nancy A. Osei',
    amount: 550,
    currency: 'GHS',
    channel: 'Flutterwave',
    status: '失败',
    failureReason: '银行通道超时',
    requestedAt: '2025-10-20 09:01',
    updatedAt: '2025-10-20 09:11',
    attempts: 2
  },
  {
    id: 'DISB-20251020032',
    loanId: 'LN202510180088',
    user: 'Samuel Adu',
    amount: 5000,
    currency: 'GHS',
    channel: 'UnionPay',
    status: '重试中',
    requestedAt: '2025-10-20 10:15',
    updatedAt: '2025-10-20 10:18',
    attempts: 3,
    failureReason: '账户校验失败'
  }
];

export const financeRepaymentsMock: FinanceRepayment[] = [
  {
    repaymentId: 'RP20251020001',
    loanId: 'LN202510200001',
    user: 'Chiamaka Eddy-okafor',
    amount: 172,
    currency: 'GHS',
    channel: 'Flutterwave',
    status: '成功',
    method: 'Momo',
    paidAt: '2025-10-20 11:22',
    recordedAt: '2025-10-20 11:25',
    ledgerEntryId: 'LEDGER-9301',
    difference: 0
  },
  {
    repaymentId: 'RP20251020007',
    loanId: 'LN202510190031',
    user: 'Nancy A. Osei',
    amount: 260,
    currency: 'GHS',
    channel: 'Bank Transfer',
    status: '异常',
    method: 'Bank Transfer',
    paidAt: '2025-10-20 13:05',
    recordedAt: '2025-10-20 13:06',
    difference: -20
  },
  {
    repaymentId: 'RP20251020015',
    loanId: 'LN202510180088',
    user: 'Samuel Adu',
    amount: 500,
    currency: 'GHS',
    channel: 'USSD',
    status: '待入账',
    method: 'USSD',
    paidAt: '2025-10-20 14:40',
    recordedAt: '2025-10-20 14:41',
    difference: 0
  }
];

export const reconciliationDiffsMock: ReconciliationDiff[] = [
  {
    id: 'DIFF-20251020-01',
    date: '2025-10-20',
    type: '放款',
    channel: 'Flutterwave',
    channelAmount: 550,
    ledgerAmount: 0,
    currency: 'GHS',
    status: '未处理',
    note: '通道失败 ledger 未记账'
  },
  {
    id: 'DIFF-20251020-04',
    date: '2025-10-20',
    type: '还款',
    channel: 'Bank Transfer',
    channelAmount: 280,
    ledgerAmount: 260,
    currency: 'GHS',
    status: '处理中',
    note: '重复回调待核实'
  },
  {
    id: 'DIFF-20251019-02',
    date: '2025-10-19',
    type: '还款',
    channel: 'UnionPay',
    channelAmount: 1000,
    ledgerAmount: 1000,
    currency: 'GHS',
    status: '已解决',
    note: '手工补记完成'
  }
];

export const applicationsMock: ApplicationRecord[] = [
  {
    id: 'LN202510200001',
    userId: 'U10001',
    product: 'InsCash Plus',
    name: 'Chiamaka Eddy-okafor',
    phone: '+233-553-001-123',
    channel: 'Google Ads',
    level: 'Level5',
    amount: 150,
    term: '7D',
    reviewer: 'Ama Owusu',
    status: '通过',
    statusCode: 'AUTO_PASS',
    submittedAt: '2025-10-20 08:06:08',
    appVersion: '1.0.17',
    tags: ['复借', '高价值'],
    repeat: true,
    riskScore: 712,
    autoDecision: 'AUTO_PASS'
  },
  {
    id: 'LN202510190031',
    userId: 'U10002',
    product: 'InsCash Max',
    name: 'Nancy A. Osei',
    phone: '+233-553-000-175',
    channel: 'Facebook Ads',
    level: 'Level4',
    amount: 550,
    term: '14D',
    reviewer: 'Kwame Boateng',
    status: '审核中',
    statusCode: 'MANUAL_PENDING',
    submittedAt: '2025-10-19 22:14:09',
    appVersion: '1.0.16',
    tags: ['OCR 待复核'],
    repeat: false,
    riskScore: 655,
    autoDecision: 'MANUAL_REVIEW'
  },
  {
    id: 'LN202510180088',
    userId: 'U10003',
    product: 'InsCash Pro',
    name: 'Samuel Adu',
    phone: '+233-553-888-002',
    channel: 'Affiliate',
    level: 'Level2',
    amount: 5000,
    term: '180D',
    reviewer: 'Efua Mensah',
    status: '拒绝',
    statusCode: 'RULE_DENY',
    submittedAt: '2025-10-18 15:33:42',
    appVersion: '1.0.15',
    tags: ['新客'],
    repeat: false,
    riskScore: 488,
    autoDecision: 'AUTO_REJECT'
  },
  {
    id: 'LN202510200145',
    userId: 'U10004',
    product: 'InsCash Plus',
    name: 'Yaw Mensah',
    phone: '+233-553-777-201',
    channel: 'Google Ads',
    level: 'Level3',
    amount: 320,
    term: '21D',
    reviewer: 'Ama Owusu',
    status: '待签署',
    statusCode: 'DOC_PENDING',
    submittedAt: '2025-10-20 09:21:54',
    appVersion: '1.0.17',
    tags: ['合同待签'],
    repeat: false,
    riskScore: 690,
    autoDecision: 'AUTO_PASS'
  }
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

const customerProfiles: ApplicationDetail['customer'][] = [
  {
    sim: 'MTN-8821',
    email: 'chiamaka@example.com',
    gender: '女',
    age: 32,
    idType: 'National ID',
    idNumber: 'GHA-718571472-2',
    education: '大学',
    maritalStatus: '未婚',
    address: 'Accra, Ghana',
    gps: '5.6037, -0.1870'
  },
  {
    sim: 'Vodafone-0021',
    email: 'nancy.osei@example.com',
    gender: '女',
    age: 35,
    idType: 'Passport',
    idNumber: 'P0021882',
    education: '硕士',
    maritalStatus: '已婚',
    address: 'Ashanti Bantama BA 52',
    gps: '6.6021, -1.6246'
  },
  {
    sim: 'AirtelTigo-7710',
    email: 'samuel.adu@example.com',
    gender: '男',
    age: 29,
    idType: 'National ID',
    idNumber: 'GHA-100200300',
    education: '本科',
    maritalStatus: '未婚',
    address: 'Kumasi, Ghana',
    gps: '6.6885, -1.6244'
  },
  {
    sim: 'MTN-1117',
    email: 'yaw.mensah@example.com',
    gender: '男',
    age: 31,
    idType: 'Driver License',
    idNumber: 'DL-9981',
    education: '本科',
    maritalStatus: '未婚',
    address: 'Tema, Ghana',
    gps: '5.669, -0.016'
  }
];

export const applicationDetailsMock: Record<string, ApplicationDetail> = Object.fromEntries(
  applicationsMock.map((application, index) => {
    const customer = customerProfiles[index % customerProfiles.length];
    const isApproved = application.status === '通过';
    return [
      application.id,
      {
        application,
        basic: {
          applyTime: application.submittedAt,
          productVersion: '2025Q4',
          deviceBrand: index % 2 === 0 ? 'Itel' : 'Samsung',
          deviceModel: index % 2 === 0 ? 'itel P671L' : 'Galaxy A21',
          appVersion: application.appVersion,
          platform: 'Android',
          source: application.channel
        },
        customer,
        approval: [
          {
            node: '机审',
            result: isApproved ? '通过' : application.status,
            operator: '规则引擎',
            time: `${application.submittedAt.split(' ')[0]} 08:06:30`
          },
          {
            node: '人工复核',
            result: application.status,
            operator: application.reviewer,
            remark: application.tags?.[0],
            time: `${application.submittedAt.split(' ')[0]} 08:08:10`
          }
        ],
        approvalSummary: {
          autoDecision: application.autoDecision ?? 'AUTO_PASS',
          manualDecision: application.status,
          riskScore: application.riskScore ?? 650,
          reasons: application.tags ?? ['规则命中：设备可信']
        },
        history: [
          { ts: application.submittedAt, event: '提交申请', actor: application.name },
          { ts: `${application.submittedAt.split(' ')[0]} 08:06`, event: '机审完成', actor: '风控系统' },
          { ts: `${application.submittedAt.split(' ')[0]} 08:08`, event: '人工审批', actor: application.reviewer }
        ],
        documents: [
          {
            type: 'OCR',
            name: '身份证（正面）',
            url: 'https://example.com/docs/ocr-front.pdf',
            updatedAt: `${application.submittedAt.split(' ')[0]} 07:58`
          },
          {
            type: 'OCR',
            name: '身份证（反面）',
            url: 'https://example.com/docs/ocr-back.pdf',
            updatedAt: `${application.submittedAt.split(' ')[0]} 07:59`
          },
          {
            type: '合同',
            name: '借款合同',
            url: 'https://example.com/docs/contract.pdf',
            updatedAt: `${application.submittedAt.split(' ')[0]} 08:10`
          }
        ]
      }
    ];
  })
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
  blacklisted: false,
  loanSummary: {
    totalLoans: 4,
    activeLoans: 2,
    outstandingAmount: 320,
    lastLoanId: 'LN202510200001',
    lastStatus: '通过',
    lastSubmittedAt: '2025-10-20 08:06:08',
    repeat: true
  },
  device: {
    deviceId: 'device-ops-01',
    platform: 'android',
    appVersion: '1.0.17',
    lastActiveAt: '2025-10-20 07:55',
    privacyConsent: true,
    locationConsent: false
  },
  kyc: {
    status: 'APPROVED',
    docType: 'National ID',
    docNumber: 'GHA-718571472-2',
    reviewer: 'KYC Bot',
    reviewedAt: '2025-10-18 10:00:00'
  },
  collectionSummary: {
    openCases: 1,
    lastBucket: 'D7',
    lastStatus: 'OPEN',
    lastActionAt: '2025-10-20 09:30:00'
  }
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
  blacklisted: false,
  loanSummary: {
    totalLoans: 2,
    activeLoans: 2,
    outstandingAmount: 550,
    lastLoanId: 'LN202510190031',
    lastStatus: '审核中',
    lastSubmittedAt: '2025-10-19 22:14:09',
    repeat: false
  },
  device: {
    deviceId: 'device-ops-02',
    platform: 'android',
    appVersion: '1.0.16',
    lastActiveAt: '2025-10-20 08:03',
    privacyConsent: true,
    locationConsent: true
  },
  kyc: {
    status: 'APPROVED',
    docType: 'Passport',
    docNumber: 'P0021882',
    reviewer: 'Nancy QA',
    reviewedAt: '2025-10-15 12:00:00'
  },
  collectionSummary: {
    openCases: 0,
    lastBucket: undefined,
    lastStatus: undefined,
    lastActionAt: undefined
  }
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
  blacklisted: false,
  loanSummary: {
    totalLoans: 1,
    activeLoans: 0,
    outstandingAmount: 0,
    lastLoanId: 'LN202510180088',
    lastStatus: '拒绝',
    lastSubmittedAt: '2025-10-18 15:33:42',
    repeat: false
  },
  device: {
    deviceId: 'device-new-01',
    platform: 'ios',
    appVersion: '1.0.15',
    lastActiveAt: '2025-10-19 21:30',
    privacyConsent: false,
    locationConsent: false
  },
  kyc: {
    status: 'PENDING',
    docType: 'National ID',
    docNumber: 'GHA-100200300',
    reviewer: undefined,
    reviewedAt: undefined
  },
  collectionSummary: {
    openCases: 0,
    lastBucket: undefined,
    lastStatus: undefined,
    lastActionAt: undefined
  }
}
};

export const disbursementsMock: DisbursementRecord[] = [
  {
    reqNo: 'REQ-001',
    loanId: 'LN202510200001',
    amount: 150,
    channel: 'mock-channel',
    status: 'SUCCESS',
    createdAt: '2025-10-20 08:10:00',
    updatedAt: '2025-10-20 08:12:00',
    failureReason: undefined,
    account: { bank: 'MockBank', accountName: 'Chiamaka', accountNumber: '1234567890' }
  },
  {
    reqNo: 'REQ-002',
    loanId: 'LN202510190031',
    amount: 550,
    channel: 'mock-channel',
    status: 'FAILED',
    createdAt: '2025-10-19 22:30:00',
    updatedAt: '2025-10-19 22:35:00',
    failureReason: '银行返回限额',
    account: { bank: 'MockBank', accountName: 'Nancy', accountNumber: '222333444' }
  }
];

export const repaymentsMock: RepaymentRecord[] = [
  {
    repaymentId: 'RP-001',
    loanId: 'LN202510200001',
    amount: 50,
    currency: 'GHS',
    channel: 'MOMO',
    status: 'POSTED',
    txnRef: 'TXN-001',
    appliedAmount: 50,
    remainingDue: 100,
    paidAt: '2025-10-21 09:00:00',
    createdAt: '2025-10-21 09:00:00'
  }
];

export const reconciliationsMock: ReconciliationRecord[] = [
  { entryId: 'LE-001', refType: 'DISBURSEMENT', refId: 'LN202510200001', status: 'POSTED', lineCount: 2, createdAt: '2025-10-20 08:11:00' },
  { entryId: 'LE-002', refType: 'REPAYMENT', refId: 'LN202510200001', status: 'POSTED', lineCount: 2, createdAt: '2025-10-21 09:00:00' }
];
export const opsProductsMock: OpsProductConfig[] = [
  {
    productId: 'P-PLUS-01',
    name: 'InsCash Plus',
    minAmount: 150,
    maxAmount: 1500,
    termOptions: '7D / 14D',
    apr: 18.5,
    allowExtension: true,
    status: '启用'
  },
  {
    productId: 'P-MAX-01',
    name: 'InsCash Max',
    minAmount: 500,
    maxAmount: 5000,
    termOptions: '30D / 45D / 60D',
    apr: 22.3,
    allowExtension: true,
    status: '启用'
  },
  {
    productId: 'P-EXP-01',
    name: 'InsCash Express',
    minAmount: 50,
    maxAmount: 300,
    termOptions: '7D',
    apr: 15.2,
    allowExtension: false,
    status: '停用'
  }
];

export const gradeConfigsMock: GradeConfig[] = [
  { grade: 'Level 1', maxCredit: 300, interestDiscount: 0, autoUpgradeDays: 45, rules: ['注册完成', 'KYC 提交'] },
  { grade: 'Level 2', maxCredit: 800, interestDiscount: 5, autoUpgradeDays: 30, rules: ['成功还款 ≥1 次'] },
  { grade: 'Level 3', maxCredit: 1500, interestDiscount: 10, autoUpgradeDays: 20, rules: ['成功还款 ≥3 次', '无逾期'] },
  { grade: 'Level 4', maxCredit: 2500, interestDiscount: 15, autoUpgradeDays: 15, rules: ['复借 5 次以上', '无逾期'] }
];

export const channelLinksMock: ChannelLinkConfig[] = [
  {
    id: 'CH-AD-GG',
    name: 'Google Ads Ghana',
    channel: 'Google',
    status: '上线',
    conversion: 12.5,
    budget: 1200,
    updatedAt: '2025-10-20 10:05'
  },
  {
    id: 'CH-AD-FB',
    name: 'Facebook Lookalike',
    channel: 'Facebook',
    status: '上线',
    conversion: 9.8,
    budget: 900,
    updatedAt: '2025-10-19 22:10'
  },
  {
    id: 'CH-AFF-001',
    name: 'Affiliate Network',
    channel: 'Affiliate',
    status: '停用',
    conversion: 3.2,
    budget: 500,
    updatedAt: '2025-10-18 18:30'
  }
];

export const messageTemplatesMock: MessageTemplateConfig[] = [
  {
    id: 'MSG-OTP',
    name: '验证码短信',
    channel: 'SMS',
    active: true,
    preview: '您的验证码为 {code}，5 分钟内有效。',
    variables: ['code']
  },
  {
    id: 'MSG-DUE',
    name: '到期提醒 WhatsApp',
    channel: 'WhatsApp',
    active: true,
    preview: '{name}，您 {dueDate} 到期的账单金额 {amount}，请及时还款。',
    variables: ['name', 'dueDate', 'amount']
  },
  {
    id: 'MSG-PROMO',
    name: '复借优惠 Push',
    channel: 'Push',
    active: false,
    preview: '完成上一笔还款即可获得 {discount}% 利率优惠！',
    variables: ['discount']
  }
];

export const approvalRulesMock: ApprovalRuleConfig[] = [
  {
    id: 'RULE-001',
    name: '高风险地区自动拒绝',
    stage: '机审',
    condition: '定位命中黑名单区域',
    action: '自动拒绝',
    owner: 'RiskOps',
    updatedAt: '2025-10-19 12:15'
  },
  {
    id: 'RULE-002',
    name: '大额人工复核',
    stage: '人审',
    condition: '额度 > 2000 或重复申请≤7天',
    action: '转人工队列',
    owner: 'LoanOps',
    updatedAt: '2025-10-18 19:22'
  },
  {
    id: 'RULE-003',
    name: '质量抽检',
    stage: '人审',
    condition: '随机 5% 通过单',
    action: '指派质检员',
    owner: 'QA Team',
    updatedAt: '2025-10-16 09:10'
  }
];

export const reportCenterMock: ReportCenterData = {
  summary: [
    { label: '当日申请', value: '1,287', delta: 5, description: '较昨日 +5%' },
    { label: '放款金额 (GHS)', value: '425,000', delta: 8, description: '较昨日 +8%' },
    { label: '首逾率 (D0)', value: '38%', delta: -2, description: '较昨日 -2pp' },
    { label: '复借率', value: '28%', delta: 3, description: '较昨日 +3pp' }
  ],
  overdueMigration: [
    { stage: 'D0→D1', todayRate: 38, yesterdayRate: 40, change: -2, note: '新客批次质量改善' },
    { stage: 'D1→D7', todayRate: 21, yesterdayRate: 22, change: -1, note: 'PTP 回收力度待提升' },
    { stage: 'D7→D15', todayRate: 12, yesterdayRate: 11, change: 1, note: 'D7 案件堆积' },
    { stage: 'D15+', todayRate: 7, yesterdayRate: 6, change: 1, note: '需触发外包策略' }
  ],
  channelFunnel: [
    { channel: 'Google Ads', installs: 820, regs: 410, applies: 287, disburses: 145, conversion: 17.7 },
    { channel: 'Facebook Ads', installs: 690, regs: 330, applies: 210, disburses: 104, conversion: 15.1 },
    { channel: 'Affiliate', installs: 320, regs: 98, applies: 70, disburses: 31, conversion: 9.7 }
  ],
  reborrowRates: [
    { segment: '高价值用户 (Level4+)', rate: 41, change: 2, volume: 380 },
    { segment: '标准用户 (Level2-3)', rate: 24, change: 1, volume: 610 },
    { segment: '新客', rate: 6, change: 0, volume: 297 }
  ],
  filters: {
    businessDate: '2025-10-20',
    channel: null,
    product: null
  },
  lastUpdated: '2025-10-20 09:45:00',
  notes: [
    '昨日渠道预算压缩 8%，今日 Google Ads 投放恢复后放款金额回升。',
    'D7→D15 档案件增加，需要与催收团队同步加强 PTP 跟进。',
    '复借用户贡献 63% 放款金额，建议继续保持复借 push 节奏。'
  ]
};

import type { AdminRole } from '../constants/roles';
import type { LoginResponse } from '../types/auth';
