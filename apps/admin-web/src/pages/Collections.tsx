import {
  Alert,
  Button,
  Card,
  DatePicker,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  List,
  message,
  Popconfirm,
  Select,
  Space,
  Spin,
  Statistic,
  Table,
  Tabs,
  Tag,
  Timeline,
  Typography,
  type TableColumnsType
} from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import { useMemo, useState } from 'react';
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { CollectionCase, CollectionCaseDetail } from '../mocks/data';
import {
  createCollectionAction,
  fetchCollectionCases,
  fetchCollectionDetail,
  fetchCollectionStats,
  type CollectionActionPayload,
  type CollectionsQuery
} from '../services/api';

const PAGE_SIZE = 5;

const Collections = () => {
  const [filters, setFilters] = useState<CollectionsQuery>({ page: 1, pageSize: PAGE_SIZE });
  const [selectedCase, setSelectedCase] = useState<CollectionCase | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const queryClient = useQueryClient();

  const listQuery = useQuery({
    queryKey: ['collection-cases', filters],
    queryFn: () => fetchCollectionCases(filters),
    placeholderData: keepPreviousData,
    staleTime: 30 * 1000
  });

  const statsQuery = useQuery({
    queryKey: ['collection-stats'],
    queryFn: () => fetchCollectionStats(),
    staleTime: 60 * 1000
  });

  const detailQuery = useQuery({
    queryKey: ['collection-case-detail', selectedCase?.caseId],
    queryFn: () => fetchCollectionDetail(selectedCase?.caseId as string),
    enabled: Boolean(selectedCase?.caseId)
  });

  const actionMutation = useMutation({
    mutationFn: (payload: CollectionActionPayload) => {
      if (!selectedCase) throw new Error('无案件');
      return createCollectionAction(selectedCase.caseId, payload);
    },
    onSuccess: (_, variables) => {
      message.success(variables.action === 'PTP' ? 'PTP 已记录' : '跟进已记录');
      queryClient.invalidateQueries({ queryKey: ['collection-case-detail', selectedCase?.caseId] });
    },
    onError: (err) => {
      message.error(err instanceof Error ? err.message : '操作失败');
    }
  });

  const detail = detailQuery.data ?? null;
  const detailLoading = Boolean(selectedCase) && (detailQuery.isPending || detailQuery.isFetching);

  const handleFilterSubmit = (values: CollectionsQuery & { daterange?: [Dayjs, Dayjs] }) => {
    const range = values.daterange;
    setFilters({
      page: 1,
      pageSize: PAGE_SIZE,
      bucket: values.bucket || undefined,
      assignee: values.assignee || undefined,
      caseId: values.caseId || undefined,
      status: values.status || undefined
    });
  };

  const handleOpenDrawer = (record: CollectionCase, tabKey: string) => {
    setSelectedCase(record);
    setActiveTab(tabKey);
  };

  const handleCloseDrawer = () => {
    setSelectedCase(null);
  };

  const columns: TableColumnsType<CollectionCase> = useMemo(
    () => [
      { title: '案件号', dataIndex: 'caseId' },
      { title: '借款人', dataIndex: 'user' },
      { title: 'Bucket', dataIndex: 'bucket' },
      { title: '逾期金额', dataIndex: 'amount', render: (value) => `₵${value}` },
      { title: '逾期天数', dataIndex: 'overdueDays' },
      { title: 'PTP 状态', dataIndex: 'ptpStatus', render: (value) => (value ? <Tag color="green">{value}</Tag> : '-') },
      { title: '分案团队', dataIndex: 'assignee' },
      { title: '到期日', dataIndex: 'due' },
      { title: '状态', dataIndex: 'status', render: (value) => <Tag color="blue">{value}</Tag> },
      {
        title: '操作',
        render: (_, record) => (
          <Space>
            <Button type="link" onClick={() => handleOpenDrawer(record, 'overview')}>
              工作台
            </Button>
            <Button type="link" onClick={() => handleOpenDrawer(record, 'ptp')}>
              记录跟进
            </Button>
            <Popconfirm title="确认转外包?" onConfirm={() => message.success(`${record.caseId} 已转外包`)}>
              <Button type="link">外包</Button>
            </Popconfirm>
          </Space>
        )
      }
    ],
    []
  );

  const renderStats = () => {
    const stats = statsQuery.data;
    if (!stats) return null;
    return (
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="案件总数" value={stats.totalCases} />
          </Card>
        </Col>
        {Object.entries(stats.buckets || {}).map(([bucket, value]) => (
          <Col span={6} key={bucket}>
            <Card>
              <Statistic title={`Bucket ${bucket}`} value={value} />
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  const followUpForm = (
    <Form
      layout="vertical"
      onFinish={(values: { action: string; result: string; note?: string }) =>
        actionMutation.mutate({ action: values.action, result: values.result, note: values.note })
      }
    >
      <Form.Item label="跟进方式" name="action" rules={[{ required: true, message: '请输入跟进方式' }]}> 
        <Input placeholder="CALL/SMS" />
      </Form.Item>
      <Form.Item label="结果" name="result" rules={[{ required: true, message: '请输入结果' }]}> 
        <Input placeholder="PTP/无人接听" />
      </Form.Item>
      <Form.Item label="备注" name="note">
        <Input.TextArea rows={3} placeholder="备注" />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={actionMutation.isPending} block>
        记录
      </Button>
    </Form>
  );

  const ptpForm = (
    <Form
      layout="vertical"
      onFinish={(values: { amount: number; promiseDate: Dayjs; note?: string; status?: string }) =>
        actionMutation.mutate({
          action: 'PTP',
          result: values.status,
          note: values.note,
          ptpAmount: values.amount,
          ptpDueAt: values.promiseDate.format('YYYY-MM-DD'),
          status: values.status
        })
      }
    >
      <Form.Item label="承诺金额" name="amount" rules={[{ required: true, message: '请输入金额' }]}> 
        <InputNumber min={1} style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="承诺日期" name="promiseDate" rules={[{ required: true, message: '请选择日期' }]}> 
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="状态" name="status">
        <Select allowClear options={['OPEN', 'PTP'].map((item) => ({ value: item, label: item }))} />
      </Form.Item>
      <Form.Item label="备注" name="note">
        <Input.TextArea rows={3} />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={actionMutation.isPending} block>
        创建 PTP
      </Button>
    </Form>
  );

  return (
    <>
      <Space direction="vertical" size={24} style={{ width: '100%' }}>
        {renderStats()}
        <Card>
          <Form layout="vertical" className="form-grid" onFinish={handleFilterSubmit} initialValues={filters}>
            <Form.Item label="案件号" name="caseId">
              <Input placeholder="输入案件号" allowClear />
            </Form.Item>
            <Form.Item label="Bucket" name="bucket">
              <Select allowClear placeholder="全部" options={['D1', 'D7', 'DP'].map((b) => ({ value: b, label: b }))} />
            </Form.Item>
            <Form.Item label="催收员" name="assignee">
              <Input placeholder="Team/Agent" allowClear />
            </Form.Item>
            <Form.Item label="状态" name="status">
              <Select allowClear placeholder="全部" options={['OPEN', 'CLOSED', 'PTP'].map((s) => ({ value: s, label: s }))} />
            </Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                查询
              </Button>
              <Button htmlType="reset" onClick={() => setFilters({ page: 1, pageSize: PAGE_SIZE })}>
                重置
              </Button>
            </Space>
          </Form>
        </Card>
        <Card>
          <Table<CollectionCase>
            rowKey="caseId"
            columns={columns}
            dataSource={listQuery.data?.list ?? []}
            loading={listQuery.isFetching}
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: listQuery.data?.total
            }}
            onChange={(pagination) =>
              setFilters((prev) => ({
                ...prev,
                page: pagination.current,
                pageSize: pagination.pageSize
              }))
            }
          />
        </Card>
      </Space>

      <Drawer
        title={selectedCase ? `${selectedCase.caseId} · ${selectedCase.user}` : '案件详情'}
        placement="right"
        width={680}
        open={!!selectedCase}
        onClose={handleCloseDrawer}
      >
        {detailLoading ? (
          <Spin />
        ) : detail ? (
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'overview',
                label: '案件概览',
                children: (
                  <Space direction="vertical" size={16} style={{ width: '100%' }}>
                    <Card>
                      <Descriptions column={2} size="small">
                        <Descriptions.Item label="借款人">{detail.summary.user}</Descriptions.Item>
                        <Descriptions.Item label="Bucket">{detail.summary.bucket}</Descriptions.Item>
                        <Descriptions.Item label="逾期金额">₵{detail.summary.amount}</Descriptions.Item>
                        <Descriptions.Item label="PTP 截止">{detail.ptpDueAt ?? '-'}</Descriptions.Item>
                        <Descriptions.Item label="剩余本金">₵{detail.ptpAmount ?? detail.summary.amount}</Descriptions.Item>
                      </Descriptions>
                    </Card>
                    <Card title="跟进记录">
                      <Timeline>
                        {detail.followUps.map((item) => (
                          <Timeline.Item key={item.ts} color="blue">
                            <strong>{item.ts}</strong>
                            <div>{item.action}</div>
                            <Typography.Text type="secondary">{item.actor}</Typography.Text>
                            <div>{item.result}</div>
                          </Timeline.Item>
                        ))}
                      </Timeline>
                    </Card>
                  </Space>
                )
              },
              {
                key: 'ptp',
                label: 'PTP / 跟进',
                children: (
                  <Space direction="vertical" size={16} style={{ width: '100%' }}>
                    <Card title="记录跟进">{followUpForm}</Card>
                    <Card title="设置 PTP">{ptpForm}</Card>
                    <Card title="PTP 记录">
                      <List
                        dataSource={detail.ptpRecords}
                        renderItem={(record) => (
                          <List.Item>
                            <List.Item.Meta
                              title={`${record.ts} · ${record.status}`}
                              description={`承诺 ${record.promiseDate} 支付 ₵${record.amount} · ${record.note ?? '-'}`}
                            />
                          </List.Item>
                        )}
                      />
                    </Card>
                  </Space>
                )
              }
            ]}
          />
        ) : (
          <Empty description="请选择案件" />
        )}
      </Drawer>
    </>
  );
};

export default Collections;
