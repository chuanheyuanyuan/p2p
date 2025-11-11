import {
  Button,
  Card,
  DatePicker,
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
  type TableColumnsType
} from 'antd';
import dayjs from 'dayjs';
import { useState, useEffect } from 'react';
import { useRequest } from 'ahooks';
import type { CollectionCase, CollectionCaseDetail } from '../mocks/data';
import {
  fetchCollectionCases,
  fetchCollectionDetail,
  type CollectionsQuery
} from '../services/api';

const PAGE_SIZE = 5;

const Collections = () => {
  const [filters, setFilters] = useState<CollectionsQuery>({ page: 1, pageSize: PAGE_SIZE });
  const [selectedCase, setSelectedCase] = useState<CollectionCase | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [detailState, setDetailState] = useState<CollectionCaseDetail | null>(null);

  const listReq = useRequest(() => fetchCollectionCases(filters), {
    refreshDeps: [filters]
  });

  const detailReq = useRequest<CollectionCaseDetail, [string]>((caseId: string) => fetchCollectionDetail(caseId), {
    manual: true,
    onSuccess: (data) => setDetailState(data)
  });

  useEffect(() => {
    if (!selectedCase) {
      setDetailState(null);
    }
  }, [selectedCase]);

  const handleOpenDrawer = (record: CollectionCase, tabKey: string) => {
    setSelectedCase(record);
    setActiveTab(tabKey);
    detailReq.run(record.caseId);
  };

  const handleCloseDrawer = () => {
    setSelectedCase(null);
  };

  const handleAddFollowUp = (values: { action: string; result: string }) => {
    if (!detailState) return;
    setDetailState({
      ...detailState,
      followUps: [
        {
          ts: dayjs().format('YYYY-MM-DD HH:mm'),
          actor: 'Sitsofe',
          action: values.action,
          result: values.result
        },
        ...detailState.followUps
      ]
    });
    message.success('已记录跟进（本地模拟）');
  };

  const handleAddPTP = (values: { amount: number; promiseDate: dayjs.Dayjs; note?: string }) => {
    if (!detailState) return;
    setDetailState({
      ...detailState,
      ptpRecords: [
        {
          ts: dayjs().format('YYYY-MM-DD HH:mm'),
          amount: values.amount,
          promiseDate: values.promiseDate.format('YYYY-MM-DD'),
          status: '有效',
          note: values.note
        },
        ...detailState.ptpRecords
      ]
    });
    message.success('PTP 已创建（本地模拟）');
  };

  const columns: TableColumnsType<CollectionCase> = [
    { title: '案件号', dataIndex: 'caseId' },
    { title: '借款人', dataIndex: 'user' },
    { title: 'Bucket', dataIndex: 'bucket' },
    { title: '逾期金额', dataIndex: 'amount', render: (value) => `₵${value}` },
    { title: '逾期天数', dataIndex: 'overdueDays' },
    { title: 'PTP 状态', dataIndex: 'ptpStatus', render: (value) => <Tag color="green">{value}</Tag> },
    { title: '分案团队', dataIndex: 'assignee' },
    { title: '到期日', dataIndex: 'due' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (value) => <Tag color="blue">{value}</Tag>
    },
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
  ];

  const detail = detailState;

  return (
    <>
      <Space direction="vertical" size={24} style={{ width: '100%' }}>
        <Card>
          <Form
            layout="vertical"
            className="form-grid"
            onFinish={(values) => setFilters({ ...filters, page: 1, ...values })}
          >
            <Form.Item label="案件号" name="caseId">
              <Input placeholder="输入案件号" allowClear />
            </Form.Item>
            <Form.Item label="Bucket" name="bucket">
              <Select options={[{ value: 'all', label: '全部' }, { value: 'D1', label: 'D1' }, { value: 'D7', label: 'D7' }]} allowClear />
            </Form.Item>
            <Form.Item label="催收员" name="assignee">
              <Select options={[{ value: 'all', label: '全部' }, { value: 'teamA', label: 'Team A' }, { value: 'teamB', label: 'Team B' }]} allowClear />
            </Form.Item>
            <Form.Item label="承诺状态" name="ptp">
              <Select options={[{ value: 'all', label: '全部' }, { value: 'valid', label: '有效' }, { value: 'broken', label: '失效' }]} allowClear />
            </Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                查询
              </Button>
              <Button htmlType="reset">重置</Button>
            </Space>
          </Form>
        </Card>
        <Card>
          <Table<CollectionCase>
            rowKey="caseId"
            columns={columns}
            dataSource={listReq.data?.list ?? []}
            loading={listReq.loading}
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: listReq.data?.total
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
        width={640}
        open={!!selectedCase}
        onClose={handleCloseDrawer}
      >
        {detailReq.loading ? (
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
                    <Statistic title="逾期金额" value={`₵${detail.summary.amount}`} />
                    <Statistic title="逾期天数" value={detail.summary.overdueDays} suffix="天" />
                    <Statistic title="PTP 状态" value={detail.summary.ptpStatus} />
                    <Timeline>
                      {detail.followUps.map((item) => (
                        <Timeline.Item key={item.ts} color="blue">
                          <strong>{item.ts}</strong>
                          <div>
                            {item.actor} - {item.action}
                          </div>
                          <div>{item.result}</div>
                        </Timeline.Item>
                      ))}
                    </Timeline>
                  </Space>
                )
              },
              {
                key: 'ptp',
                label: 'PTP 记录',
                children: (
                  <Space direction="vertical" size={16} style={{ width: '100%' }}>
                    <Form
                      layout="vertical"
                      onFinish={handleAddPTP}
                      initialValues={{ promiseDate: dayjs().add(2, 'day') }}
                    >
                      <Form.Item label="承诺金额 (GHS)" name="amount" rules={[{ required: true }]}> 
                        <InputNumber style={{ width: '100%' }} min={0} />
                      </Form.Item>
                      <Form.Item label="承诺日期" name="promiseDate" rules={[{ required: true }]}> 
                        <DatePicker style={{ width: '100%' }} />
                      </Form.Item>
                      <Form.Item label="备注" name="note">
                        <Input.TextArea rows={2} />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>
                        新增承诺
                      </Button>
                    </Form>
                    <List
                      dataSource={detail.ptpRecords}
                      renderItem={(record) => (
                        <List.Item>
                          <List.Item.Meta
                            title={`${record.ts} · 承诺 ₵${record.amount} · ${record.promiseDate}`}
                            description={record.note}
                          />
                          <Tag color={record.status === '有效' ? 'green' : 'red'}>{record.status}</Tag>
                        </List.Item>
                      )}
                    />
                  </Space>
                )
              },
              {
                key: 'calls',
                label: '外呼记录',
                children: (
                  <List
                    dataSource={detail.callLogs}
                    renderItem={(call) => (
                      <List.Item>
                        <List.Item.Meta
                          title={`${call.ts} · ${call.channel}`}
                          description={`${call.duration} · ${call.note}`}
                        />
                      </List.Item>
                    )}
                  />
                )
              },
              {
                key: 'new',
                label: '新增跟进',
                children: (
                  <Form layout="vertical" onFinish={handleAddFollowUp}>
                    <Form.Item label="跟进行为" name="action" rules={[{ required: true }]}> 
                      <Input.TextArea rows={3} placeholder="如：外呼 / 短信 / 上门" />
                    </Form.Item>
                    <Form.Item label="结果" name="result" rules={[{ required: true }]}> 
                      <Input.TextArea rows={3} placeholder="如：客户承诺、无人接听" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block>
                      记录
                    </Button>
                  </Form>
                )
              }
            ]}
          />
        ) : (
          <p>请选择一个案件查看详情。</p>
        )}
      </Drawer>
    </>
  );
};

export default Collections;
