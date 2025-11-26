from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SessionUser(BaseModel):
    id: str
    name: str
    email: str
    title: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
    user: SessionUser
    roles: List[str]
    permissions: List[str]


class ApplicationRecord(BaseModel):
    id: str
    userId: str
    product: str
    productId: str
    name: str = '未知借款人'
    phone: Optional[str] = None
    channel: str = 'unknown'
    level: str = 'Level1'
    amount: float
    term: str
    reviewer: str = '系统'
    status: str
    statusCode: Optional[str] = None
    submittedAt: str
    appVersion: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    repeat: bool = False
    riskScore: Optional[int] = None
    autoDecision: Optional[str] = None
    outstandingAmount: Optional[Decimal] = None
    originalAmount: Optional[Decimal] = None
    lastPaidAt: Optional[str] = None


class ApplicationBasicInfo(BaseModel):
    applyTime: str
    productVersion: str
    deviceBrand: str
    deviceModel: str
    appVersion: Optional[str] = None
    platform: str = 'android'
    source: str = 'app'


class ApplicationCustomerProfile(BaseModel):
    sim: str = 'unknown'
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    idType: Optional[str] = None
    idNumber: Optional[str] = None
    education: Optional[str] = None
    maritalStatus: Optional[str] = None
    address: Optional[str] = None
    gps: Optional[str] = None


class ApprovalNode(BaseModel):
    node: str
    result: str
    operator: str
    remark: Optional[str] = None
    time: str


class ApprovalSummary(BaseModel):
    autoDecision: Optional[str] = None
    manualDecision: Optional[str] = None
    riskScore: Optional[int] = None
    reasons: List[str] = Field(default_factory=list)


class ApplicationHistoryEntry(BaseModel):
    ts: str
    event: str
    actor: str


class ApplicationDocument(BaseModel):
    type: str
    name: str
    url: str
    updatedAt: str


class ApplicationDetail(BaseModel):
    application: ApplicationRecord
    basic: ApplicationBasicInfo
    customer: ApplicationCustomerProfile
    approval: List[ApprovalNode]
    approvalSummary: ApprovalSummary
    history: List[ApplicationHistoryEntry]
    documents: List[ApplicationDocument]


class PaginatedApplications(BaseModel):
    list: List[ApplicationRecord]
    total: int


class BorrowerLoanSummary(BaseModel):
    totalLoans: int = 0
    activeLoans: int = 0
    outstandingAmount: Optional[Decimal] = None
    lastLoanId: Optional[str] = None
    lastStatus: Optional[str] = None
    lastSubmittedAt: Optional[str] = None
    repeat: bool = False


class BorrowerDeviceInfo(BaseModel):
    deviceId: Optional[str] = None
    platform: Optional[str] = None
    appVersion: Optional[str] = None
    lastActiveAt: Optional[str] = None
    privacyConsent: bool = False
    locationConsent: bool = False


class BorrowerKycInfo(BaseModel):
    status: str = 'UNKNOWN'
    docType: Optional[str] = None
    docNumber: Optional[str] = None
    reviewer: Optional[str] = None
    reviewedAt: Optional[str] = None


class BorrowerCollectionSummary(BaseModel):
    openCases: int = 0
    lastBucket: Optional[str] = None
    lastStatus: Optional[str] = None
    lastActionAt: Optional[str] = None


class UserProfile(BaseModel):
    userId: str
    name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    level: str = 'Level1'
    kycStatus: str = 'UNKNOWN'
    registerDate: Optional[str] = None
    lastLogin: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    riskFlags: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    gps: Optional[str] = None
    blacklisted: bool = False
    loanSummary: Optional[BorrowerLoanSummary] = None
    device: Optional[BorrowerDeviceInfo] = None
    kyc: Optional[BorrowerKycInfo] = None
    collectionSummary: Optional[BorrowerCollectionSummary] = None


class CollectionCaseItem(BaseModel):
    caseId: str
    user: str
    bucket: str
    amount: float
    principalDue: float
    overdueDays: int
    ptpStatus: Optional[str] = None
    assignee: Optional[str] = None
    channel: Optional[str] = None
    due: Optional[str] = None
    status: str


class CollectionFollowUp(BaseModel):
    ts: str
    actor: str
    action: str
    result: Optional[str] = None


class CollectionPTPRecord(BaseModel):
    ts: str
    amount: float
    promiseDate: Optional[str] = None
    status: str
    note: Optional[str] = None


class CollectionContact(BaseModel):
    phone: Optional[str] = None
    altPhone: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[str] = None


class CollectionCaseDetail(BaseModel):
    summary: CollectionCaseItem
    contact: CollectionContact
    followUps: List[CollectionFollowUp]
    ptpRecords: List[CollectionPTPRecord]
    ptpDueAt: Optional[str] = None
    ptpAmount: Optional[float] = None


class CollectionActionRequest(BaseModel):
    action: str
    result: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None
    ptpAmount: Optional[float] = None
    ptpDueAt: Optional[str] = None


class CollectionStats(BaseModel):
    totalCases: int
    buckets: Dict[str, int]
    statuses: Dict[str, int]


class PaginatedCollectionCases(BaseModel):
    list: List[CollectionCaseItem]
    total: int


class DashboardKpi(BaseModel):
    label: str
    value: str
    delta: str


class DashboardOverdue(BaseModel):
    rate: float
    dueToday: int
    repaid: int
    yesterdayRate: float
    progress: float


class DashboardRecovery(BaseModel):
    cases: int
    assigned: int
    note: str


class DashboardToday(BaseModel):
    installs: int
    regs: int
    logins: int
    applies: int
    disburses: int
    repayments: int


class DashboardConversion(BaseModel):
    percent: float
    numerator: int
    denominator: int


class ChannelFunnelRow(BaseModel):
    channel: str
    installs: int
    registrations: int
    applications: int
    disbursements: int
    spend: str
    conversion: float = Field(default=0.0, description='disburse / apply 转化率，百分比')


class DashboardStats(BaseModel):
    kpis: List[DashboardKpi]
    overdue: DashboardOverdue
    recovery: DashboardRecovery
    today: DashboardToday
    conversion: DashboardConversion
    channelFunnel: List[ChannelFunnelRow] = Field(default_factory=list)


class ReportSummaryItem(BaseModel):
    label: str
    value: str
    delta: float = 0.0
    description: str = ''


class OverdueMigrationRow(BaseModel):
    stage: str
    todayRate: float
    yesterdayRate: float
    change: float
    note: Optional[str] = None


class ReborrowRateRow(BaseModel):
    segment: str
    rate: float
    change: float
    volume: int


class ReportCenterResponse(BaseModel):
    summary: List[ReportSummaryItem]
    overdueMigration: List[OverdueMigrationRow]
    channelFunnel: List[ChannelFunnelRow]
    reborrowRates: List[ReborrowRateRow]
    filters: dict
    lastUpdated: str
    notes: List[str] = Field(default_factory=list)


class DailyStat(BaseModel):
    date: date
    installs: int = 0
    regs: int = 0
    logins: int = 0
    applies: int = 0
    disburses: int = 0
    repayments: int = 0
    amount: float = 0


class PaginatedDailyStats(BaseModel):
    list: List[DailyStat]
    total: int


class DailyStatsExportResponse(BaseModel):
    taskId: str


class ExportResponse(BaseModel):
    taskId: str


class DisbursementRecord(BaseModel):
    reqNo: str
    loanId: str
    amount: Decimal
    channel: str
    status: str
    failureReason: Optional[str] = None
    createdAt: str
    updatedAt: str
    account: dict


class RepaymentRecord(BaseModel):
    repaymentId: str
    loanId: str
    amount: Decimal
    currency: str
    channel: str
    status: str
    txnRef: str
    appliedAmount: Decimal
    remainingDue: Decimal
    paidAt: str
    createdAt: str


class ReconciliationRecord(BaseModel):
    entryId: str
    refType: str
    refId: str
    status: str
    lineCount: int
    createdAt: str


class PaginatedDisbursements(BaseModel):
    list: List[DisbursementRecord]
    total: int


class PaginatedRepayments(BaseModel):
    list: List[RepaymentRecord]
    total: int


class PaginatedReconciliations(BaseModel):
    list: List[ReconciliationRecord]
    total: int
