import { Alert, Card, Col, Descriptions, Empty, Row, Space, Spin, Tag, Typography } from 'antd';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import type { UserProfile as UserProfileType } from '../mocks/data';
import { fetchUserProfile } from '../services/api';
import { formatCurrency, maskPhone } from '../utils/format';

const UserProfile = () => {
  const { userId = '' } = useParams();

  const { data, isPending, error } = useQuery({
    queryKey: ['user-profile', userId],
    queryFn: () => fetchUserProfile(userId),
    enabled: Boolean(userId)
  });

  if (isPending) {
    return (
      <div style={{ textAlign: 'center', padding: '48px 0' }}>
        <Spin />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message="获取用户档案失败" description={(error as Error).message} />;
  }

  if (!data) {
    return (
      <Card>
        <Empty description={`未找到用户 ${userId}`} />
      </Card>
    );
  }

  const profile = data;
  const loanSummary = profile.loanSummary;
  const device = profile.device;
  const kyc = profile.kyc;
  const collectionSummary = profile.collectionSummary;
  const summaryMetrics = [
    { label: '累计贷款', value: `${loanSummary?.totalLoans ?? 0} 笔` },
    { label: '活跃贷款', value: `${loanSummary?.activeLoans ?? 0} 笔` },
    {
      label: '剩余本金',
      value: loanSummary?.outstandingAmount ? formatCurrency(Number(loanSummary.outstandingAmount)) : '-'
    },
    { label: '催收案件', value: `${collectionSummary?.openCases ?? 0} 个` }
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Row gutter={[16, 16]}>
          {summaryMetrics.map((metric) => (
            <Col key={metric.label} xs={12} md={6}>
              <div>
                <Typography.Text type="secondary">{metric.label}</Typography.Text>
                <Typography.Title level={4} style={{ margin: 0 }}>
                  {metric.value}
                </Typography.Title>
              </div>
            </Col>
          ))}
        </Row>
      </Card>
      <Row gutter={16} wrap>
        <Col xs={24} lg={12}>
          <Card title="身份信息">
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="用户 ID">{profile.userId}</Descriptions.Item>
              <Descriptions.Item label="姓名">{profile.name}</Descriptions.Item>
              <Descriptions.Item label="性别">{profile.gender ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="手机号">{maskPhone(profile.phone)}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{profile.email ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="地址">{profile.address ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="GPS">{profile.gps ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="注册时间">{profile.registerDate ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="最近登录">{profile.lastLogin ?? '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Card title="贷款概览">
              <Descriptions column={2} size="small">
                <Descriptions.Item label="等级">{profile.level}</Descriptions.Item>
                <Descriptions.Item label="复借">{loanSummary?.repeat ? '是' : '否'}</Descriptions.Item>
                <Descriptions.Item label="最近贷款">{loanSummary?.lastLoanId ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="状态">{loanSummary?.lastStatus ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="提交时间">{loanSummary?.lastSubmittedAt ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="黑名单">{profile.blacklisted ? '是' : '否'}</Descriptions.Item>
              </Descriptions>
            </Card>
            <Card title="催收摘要">
              <Descriptions column={2} size="small">
                <Descriptions.Item label="开放案件">{collectionSummary?.openCases ?? 0}</Descriptions.Item>
                <Descriptions.Item label="最新 Bucket">{collectionSummary?.lastBucket ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="最新状态">{collectionSummary?.lastStatus ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="最后动作">{collectionSummary?.lastActionAt ?? '-'}</Descriptions.Item>
              </Descriptions>
            </Card>
          </Space>
        </Col>
      </Row>
      <Row gutter={16} wrap>
        <Col xs={24} lg={12}>
          <Card title="风控状态">
            <ul className="stat-list">
              <li>
                <span>KYC 状态</span>
                <strong>{profile.kycStatus}</strong>
              </li>
              <li>
                <span>风险标签</span>
                <strong>{profile.riskFlags.length}</strong>
              </li>
              <li>
                <span>自定义标签</span>
                <strong>{profile.tags.length}</strong>
              </li>
            </ul>
            <Typography.Text type="secondary">标签</Typography.Text>
            <div style={{ marginTop: 8 }}>
              {profile.tags.map((tag: string) => (
                <Tag key={tag} color="blue">
                  {tag}
                </Tag>
              ))}
            </div>
            <Typography.Text type="secondary">风险提示</Typography.Text>
            <div style={{ marginTop: 8 }}>
              {profile.riskFlags.map((flag: string) => (
                <Tag key={flag} color="orange">
                  {flag}
                </Tag>
              ))}
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Card title="KYC 信息">
              <Descriptions column={2} size="small">
                <Descriptions.Item label="状态">{kyc?.status ?? profile.kycStatus}</Descriptions.Item>
                <Descriptions.Item label="证件">{kyc?.docNumber ? `${kyc?.docType} · ${kyc?.docNumber}` : '-'}</Descriptions.Item>
                <Descriptions.Item label="审核人">{kyc?.reviewer ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="审核时间">{kyc?.reviewedAt ?? '-'}</Descriptions.Item>
              </Descriptions>
            </Card>
            <Card title="设备信息">
              <Descriptions column={2} size="small">
                <Descriptions.Item label="设备 ID">{device?.deviceId ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="平台">{device?.platform ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="App 版本">{device?.appVersion ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="最近活跃">{device?.lastActiveAt ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="隐私授权">{device?.privacyConsent ? '已授权' : '未授权'}</Descriptions.Item>
                <Descriptions.Item label="定位授权">{device?.locationConsent ? '已授权' : '未授权'}</Descriptions.Item>
              </Descriptions>
            </Card>
          </Space>
        </Col>
      </Row>
    </Space>
  );
};

export default UserProfile;
