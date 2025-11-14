import { Alert, Badge, Card, Col, Descriptions, Empty, List, Row, Space, Spin, Tabs, Tag, Timeline, Typography } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import type { ApplicationDetail as ApplicationDetailType, ApprovalNode, ApplicationHistoryEntry } from '../mocks/data';
import { fetchApplicationById } from '../services/api';
import { formatCurrency, maskPhone } from '../utils/format';

const ApplicationDetail = () => {
  const { id = '' } = useParams();
  const navigate = useNavigate();

  const { data, isPending, error } = useQuery({
    queryKey: ['application-detail', id],
    queryFn: () => fetchApplicationById(id),
    enabled: Boolean(id)
  });

  if (isPending) {
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

  const { application, basic, approval, approvalSummary, history, customer, documents } = data;
  const docList = documents ?? [];
  const statusColorMap: Record<string, string> = {
    通过: 'green',
    审核中: 'gold',
    拒绝: 'red',
    待签署: 'blue'
  };

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
                <Card
                  title="贷款信息"
                  extra={
                    <Space size="middle">
                      <Badge color={statusColorMap[application.status] ?? 'default'} text={application.status} />
                      <a onClick={() => navigate(`/users/${application.userId}`)}>查看用户档案</a>
                    </Space>
                  }
                >
                  <Descriptions column={2} bordered size="small">
                    <Descriptions.Item label="贷款编号">{application.id}</Descriptions.Item>
                    <Descriptions.Item label="申请时间">{basic.applyTime}</Descriptions.Item>
                    <Descriptions.Item label="产品">{application.product}</Descriptions.Item>
                    <Descriptions.Item label="金额">{formatCurrency(application.amount)}</Descriptions.Item>
                    <Descriptions.Item label="期限">{application.term}</Descriptions.Item>
                    <Descriptions.Item label="渠道">{basic.source}</Descriptions.Item>
                    <Descriptions.Item label="App 版本">{basic.appVersion}</Descriptions.Item>
                    <Descriptions.Item label="设备">{`${basic.deviceBrand} / ${basic.deviceModel}`}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col xs={24} lg={10}>
                <Space direction="vertical" size={16} style={{ width: '100%' }}>
                  <Card title="客户信息">
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="姓名">{application.name}</Descriptions.Item>
                      <Descriptions.Item label="手机号">{maskPhone(application.phone)}</Descriptions.Item>
                      <Descriptions.Item label="邮箱">{customer.email}</Descriptions.Item>
                      <Descriptions.Item label="SIM">{customer.sim}</Descriptions.Item>
                      <Descriptions.Item label="证件">{`${customer.idType} · ${customer.idNumber}`}</Descriptions.Item>
                      <Descriptions.Item label="教育/婚姻">{`${customer.education} · ${customer.maritalStatus}`}</Descriptions.Item>
                      <Descriptions.Item label="地址">{customer.address}</Descriptions.Item>
                      <Descriptions.Item label="GPS">{customer.gps}</Descriptions.Item>
                    </Descriptions>
                  </Card>
                  <Card title="审批摘要">
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="机审结果">{approvalSummary.autoDecision}</Descriptions.Item>
                      <Descriptions.Item label="人工结果">{approvalSummary.manualDecision}</Descriptions.Item>
                      <Descriptions.Item label="风险评分">{approvalSummary.riskScore}</Descriptions.Item>
                      <Descriptions.Item label="命中原因">
                        <Space size={4} wrap>
                          {approvalSummary.reasons.map((reason) => (
                            <Tag key={reason}>{reason}</Tag>
                          ))}
                        </Space>
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Space>
              </Col>
            </Row>
          )
        },
        {
          key: 'approval',
          label: '审批信息',
          children: (
            <Card>
              <Descriptions column={2} size="small" style={{ marginBottom: 16 }}>
                <Descriptions.Item label="状态">{application.status}</Descriptions.Item>
                <Descriptions.Item label="状态码">{application.statusCode ?? '-'}</Descriptions.Item>
                <Descriptions.Item label="机审">{approvalSummary.autoDecision}</Descriptions.Item>
                <Descriptions.Item label="人工">{approvalSummary.manualDecision}</Descriptions.Item>
              </Descriptions>
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
        },
        {
          key: 'documents',
          label: '凭证',
          children: (
            <Card>
              {docList.length === 0 ? (
                <Empty description="暂无凭证" />
              ) : (
                <List
                  dataSource={docList}
                  renderItem={(doc) => (
                    <List.Item actions={[<a key="download" href={doc.url}>下载</a>]}>
                      <List.Item.Meta title={doc.name} description={`${doc.type} · 更新于 ${doc.updatedAt}`} />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          )
        }
      ]}
    />
  );
};

export default ApplicationDetail;
