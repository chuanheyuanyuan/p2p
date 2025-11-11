import { Alert, Card, Col, Descriptions, Empty, Row, Spin, Tabs, Timeline, Typography } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { useRequest } from 'ahooks';
import type { ApplicationDetail as ApplicationDetailType, ApprovalNode, ApplicationHistoryEntry } from '../mocks/data';
import { fetchApplicationById } from '../services/api';

const ApplicationDetail = () => {
  const { id = '' } = useParams();
  const navigate = useNavigate();

  const { data, loading, error } = useRequest<ApplicationDetailType | undefined, []>(() => fetchApplicationById(id), {
    ready: Boolean(id)
  });

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '48px 0' }}>
        <Spin />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message="拉取申请详情失败" description={(error as Error).message} />;
  }

  if (!data) {
    return (
      <Card>
        <Empty description={`未找到编号为 ${id} 的申请`} />
      </Card>
    );
  }

  const { application, basic, approval, history } = data;

  return (
    <Tabs
      defaultActiveKey="base"
      items={[
        {
          key: 'base',
          label: '客户信息',
          children: (
            <Row gutter={16} wrap>
              <Col xs={24} lg={14}>
                <Card title="基本信息" extra={<a onClick={() => navigate(`/users/${application.userId}`)}>查看用户档案</a>}>
                  <Descriptions column={2} bordered size="small">
                    <Descriptions.Item label="贷款编号">{application.id}</Descriptions.Item>
                    <Descriptions.Item label="申请时间">{basic.applyTime}</Descriptions.Item>
                    <Descriptions.Item label="产品名称">{application.product}</Descriptions.Item>
                    <Descriptions.Item label="贷款金额">₵{application.amount}</Descriptions.Item>
                    <Descriptions.Item label="用户姓名">{application.name}</Descriptions.Item>
                    <Descriptions.Item label="等级">{application.level}</Descriptions.Item>
                    <Descriptions.Item label="渠道">{basic.source}</Descriptions.Item>
                    <Descriptions.Item label="是否复借">{basic.repeated ? '是' : '否'}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col xs={24} lg={10}>
                <Card title="设备数据">
                  <ul className="stat-list">
                    <li>
                      <span>设备品牌</span>
                      <strong>{basic.deviceBrand}</strong>
                    </li>
                    <li>
                      <span>设备型号</span>
                      <strong>{basic.deviceModel}</strong>
                    </li>
                    <li>
                      <span>App 版本</span>
                      <strong>{basic.appVersion}</strong>
                    </li>
                    <li>
                      <span>产品版本</span>
                      <strong>{basic.productVersion}</strong>
                    </li>
                  </ul>
                </Card>
              </Col>
            </Row>
          )
        },
        {
          key: 'approval',
          label: '审批信息',
          children: (
            <Card>
              <Timeline mode="left">
                {approval.map((node: ApprovalNode) => (
                  <Timeline.Item key={node.node} label={node.time} color={node.result === '通过' ? 'green' : 'red'}>
                    <Typography.Text strong>{node.node}</Typography.Text>
                    <div>结果：{node.result}</div>
                    <div>操作人：{node.operator}</div>
                    {node.remark && <div>备注：{node.remark}</div>}
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )
        },
        {
          key: 'history',
          label: '历史记录',
          children: (
            <Card>
              <Timeline>
                {history.map((item: ApplicationHistoryEntry) => (
                  <Timeline.Item key={item.ts} color="blue">
                    <strong>{item.ts}</strong>
                    <div>{item.event}</div>
                    <Typography.Text type="secondary">{item.actor}</Typography.Text>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )
        }
      ]}
    />
  );
};

export default ApplicationDetail;
