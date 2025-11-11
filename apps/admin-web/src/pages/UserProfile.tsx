import { Alert, Card, Col, Descriptions, Empty, Row, Space, Spin, Tag, Typography } from 'antd';
import { useParams } from 'react-router-dom';
import { useRequest } from 'ahooks';
import type { UserProfile as UserProfileType } from '../mocks/data';
import { fetchUserProfile } from '../services/api';

const UserProfile = () => {
  const { userId = '' } = useParams();

  const { data, loading, error } = useRequest<UserProfileType | undefined, []>(() => fetchUserProfile(userId), {
    ready: Boolean(userId)
  });

  if (loading) {
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

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Row gutter={16} wrap>
        <Col xs={24} lg={14}>
          <Card title="身份信息">
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="用户 ID">{profile.userId}</Descriptions.Item>
              <Descriptions.Item label="姓名">{profile.name}</Descriptions.Item>
              <Descriptions.Item label="性别">{profile.gender}</Descriptions.Item>
              <Descriptions.Item label="手机号">{profile.phone}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{profile.email}</Descriptions.Item>
              <Descriptions.Item label="地址">{profile.address}</Descriptions.Item>
              <Descriptions.Item label="GPS">{profile.gps}</Descriptions.Item>
              <Descriptions.Item label="注册时间">{profile.registerDate}</Descriptions.Item>
              <Descriptions.Item label="最近登录">{profile.lastLogin}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="风控状态">
            <ul className="stat-list">
              <li>
                <span>等级</span>
                <strong>{profile.level}</strong>
              </li>
              <li>
                <span>KYC 状态</span>
                <strong>{profile.kycStatus}</strong>
              </li>
              <li>
                <span>黑名单</span>
                <strong>{profile.blacklisted ? '是' : '否'}</strong>
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
      </Row>
    </Space>
  );
};

export default UserProfile;
