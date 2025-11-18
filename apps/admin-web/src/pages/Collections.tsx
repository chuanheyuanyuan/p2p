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
import { useEffect, useMemo, useState } from 'react';
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

const BUCKET_OPTIONS = ['D1', 'D3', 'D7', 'D15', 'D30', 'D60'].map((bucket) => ({ label: bucket, value: bucket }));
const CASE_STATUS_OPTIONS = [
  { label: '跟进中', value: 'OPEN' },
  { label: '已承诺', value: 'PROMISE' },
  { label: 'PTP 有效', value: 'PTP' },
  { label: '已结清', value: 'PAID' },
  { label: '已关闭', value: 'CLOSED' }
];

interface FollowUpFormValues {
  action: string;
  result: string;
  status?: string;
  note?: string;
}

interface PtpFormValues {
  amount: number;
  promiseDate: dayjs.Dayjs;
  note?: string;
  status?: string;
}

const Collections = () => {
  const [filters, setFilters] = useState<CollectionsQuery>({ page: 1, pageSize: PAGE_SIZE });
  const [selectedCase, setSelectedCase] = useState<CollectionCase | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [filterForm] = Form.useForm();
  const [followForm] = Form.useForm<FollowUpFormValues>();
  const [ptpForm] = Form.useForm<PtpFormValues>();
  const queryClient = useQueryClient();
  const listQuery = useQuery({
    queryKey: ['collection-cases', filters],
    queryFn: () => fetchCollectionCases(filters),
    placeholderData: keepPreviousData,
    staleTime: 30 * 1000
  });

  const detailQuery = useQuery({
    queryKey: ['collection-case-detail', selectedCase?.caseId],
    queryFn: () => fetchCollectionDetail(selectedCase?.caseId as string),
    enabled: Boolean(selectedCase?.caseId)
  });
  const detailLoading = Boolean(selectedCase) && (detailQuery.isPending || detailQuery.isFetching);
  const statsQuery = useQuery({
    queryKey: ['collection-stats'],
    queryFn: fetchCollectionStats,
    staleTime: 5 * 60 * 1000
  });

  const statsBuckets = useMemo(() => Object.entries(statsQuery.data?.buckets ?? {}), [statsQuery.data]);
  const statsStatuses = useMemo(() => Object.entries(statsQuery.data?.statuses ?? {}), [statsQuery.data]);

  const updateCaseDetailCache = (caseId: string, detail: CollectionCaseDetail) => {
    queryClient.setQueryData(['collection-case-detail', caseId], detail);
    queryClient.invalidateQueries({ queryKey: ['collection-cases'] });
    setSelectedCase((prev) => {
      if (!prev || prev.caseId !== caseId) return prev;
      return {
        ...prev,
        status: detail.summary.status ?? prev.status,
        ptpStatus: detail.summary.ptpStatus ?? prev.ptpStatus
      };
    });
  };

  const followUpMutation = useMutation({
    mutationFn: ({
      caseId,
      payload
    }: {
      caseId: string;
      payload: CollectionActionPayload;
    }) => createCollectionAction(caseId, payload),
    onSuccess: (data, variables) => {
      updateCaseDetailCache(variables.caseId, data);
      message.success('跟进已记录');
      followForm.resetFields();
    },
    onError: (error) => {
      console.error('create follow up failed', error);
      message.error('创建跟进失败，请稍后再试');
    }
  });

  const ptpMutation = useMutation({
    mutationFn: ({
      caseId,
      payload
    }: {
      caseId: string;
      payload: CollectionActionPayload;
    }) => createCollectionAction(caseId, payload),
    onSuccess: (data, variables) => {
      updateCaseDetailCache(variables.caseId, data);
      ptpForm.setFieldsValue({
        amount: undefined,
        promiseDate: dayjs().add(2, 'day'),
        note: undefined,
        status: 'PROMISE'
      });
      message.success('PTP 已创建');
    },
    onError: (error) => {
      console.error('create ptp failed', error);
      message.error('创建 PTP 失败，请稍后再试');
    }
  });

  const handleOpenDrawer = (record: CollectionCase, tabKey: string) => {
    setSelectedCase(record);
    setActiveTab(tabKey);
    followForm.resetFields();
    ptpForm.setFieldsValue({
      amount: undefined,
      promiseDate: dayjs().add(2, 'day'),
      note: undefined,
      status: 'PROMISE'
    });
  };

  useEffect(() => {
    if (!selectedCase) {
      followForm.resetFields();
      ptpForm.resetFields();
    }
  }, [selectedCase, followForm, ptpForm]);

  const handleAddFollowUp = (values: FollowUpFormValues) => {
    if (!selectedCase) return;
    followUpMutation.mutate({
      caseId: selectedCase.caseId,
      payload: {
        action: values.action,
        result: values.result,
        note: values.note,
        status: values.status
      }
    });
  };

  const handleAddPTP = (values: PtpFormValues) => {
    if (!selectedCase) return;
    ptpMutation.mutate({
      caseId: selectedCase.caseId,
      payload: {
        action: 'PTP',
        result: 'Promise To Pay',
        note: values.note,
        status: values.status ?? 'PROMISE',
        ptpAmount: values.amount,
        ptpDueAt: values.promiseDate.startOf('day').format('YYYY-MM-DDTHH:mm:ss')
      }
    });
  };

  const handleCloseDrawer = () => {
    setSelectedCase(null);
    setActiveTab('overview');
  };

  const handleFilterSubmit = (values: Partial<CollectionsQuery>) => {
    setFilters((prev) => ({
      ...prev,
      page: 1,
      caseId: values.caseId || undefined,
      bucket: values.bucket || undefined,
      assignee: values.assignee || undefined,
      status: values.status || undefined
    }));
  };

  const handleFilterReset = () => {
    filterForm.resetFields();
    setFilters({ page: 1, pageSize: PAGE_SIZE });
  };

  const renderDistribution = (entries: [string, number][]) => {
    if (!entries.length) return <span>暂无数据</span>;
    return (
      <Space size={8} wrap>
        {entries.map(([key, count]) => (
          <Tag key={key} color="blue">
            {key}: {count}
          </Tag>
        ))}
      </Space>
    );
  };

  const statusTag = (value?: string) => {
    if (!value) return <Tag color="default">-</Tag>;
    const colorMap: Record<string, string> = {
      OPEN: 'blue',
      PROMISE: 'cyan',
      PTP: 'green',
      PAID: 'green',
      CLOSED: 'red'
    };
    return <Tag color={colorMap[value] ?? 'blue'}>{value}</Tag>;
  };

  const columns: TableColumnsType<CollectionCase> = [
    { title: '案件号', dataIndex: 'caseId' },
    { title: '借款人', dataIndex: 'user' },
    { title: 'Bucket', dataIndex: 'bucket' },
    { title: '逾期金额', dataIndex: 'amount', render: (value: number) => `₵${value?.toFixed?.(2) ?? value}` },
    { title: '逾期天数', dataIndex: 'overdueDays' },
    {
      title: 'PTP 状态',
      dataIndex: 'ptpStatus',
      render: (value?: string) => (value ? <Tag color="green">{value}</Tag> : '-')
    },
    { title: '分案团队', dataIndex: 'assignee' },
    { title: '到期日', dataIndex: 'due' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (value?: string) => statusTag(value)
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

  const detail = detailQuery.data ?? null;

  return (
    <>
      <Space direction="vertical" size={24} style={{ width: '100%' }}>
        <Card>
          <Form
            form={filterForm}
            layout="vertical"
            className="form-grid"
            onFinish={handleFilterSubmit}
          >
            <Form.Item label="案件号" name="caseId">
              <Input placeholder="输入案件号" allowClear />
            </Form.Item>
            <Form.Item label="Bucket" name="bucket">
              <Select options={BUCKET_OPTIONS} placeholder="选择 Bucket" allowClear />
            </Form.Item>
            <Form.Item label="催收员" name="assignee">
              <Input placeholder="输入催收员/团队" allowClear />
            </Form.Item>
            <Form.Item label="案件状态" name="status">
              <Select options={CASE_STATUS_OPTIONS} placeholder="选择状态" allowClear />
            </Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                查询
              </Button>
              <Button htmlType="button" onClick={handleFilterReset}>
                重置
              </Button>
            </Space>
          </Form>
        </Card>
        <Card
          loading={statsQuery.isLoading}
          title="案件池概览"
          extra={
            <Button size="small" onClick={() => statsQuery.refetch()} loading={statsQuery.isFetching}>
              刷新
            </Button>
          }
        >
          <Space size={32} wrap>
            <Statistic title="案件总数" value={statsQuery.data?.totalCases ?? 0} />
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>Bucket 分布</div>
              {renderDistribution(statsBuckets)}
            </div>
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>状态分布</div>
              {renderDistribution(statsStatuses)}
            </div>
          </Space>
        </Card>
        <Card>
          <Table<CollectionCase>
            rowKey="caseId"
            columns={columns}
            dataSource={listQuery.data?.list ?? []}
            loading={listQuery.isLoading || listQuery.isFetching}
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: listQuery.data?.total
            }}
            onChange={(pagination) =>
              setFilters((prev) => ({
                ...prev,
                page: pagination.current ?? 1,
                pageSize: pagination.pageSize ?? PAGE_SIZE
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
                    <Space size={24} wrap>
                      <Statistic title="逾期金额" value={`₵${detail.summary.amount}`} />
                      <Statistic title="逾期天数" value={detail.summary.overdueDays} suffix="天" />
                      <Statistic title="PTP 状态" value={detail.summary.ptpStatus ?? '暂无'} />
                      <Statistic title="当前状态" value={selectedCase?.status ?? '--'} />
                    </Space>
                    <Card size="small" title="联系方式">
                      <Space direction="vertical">
                        <span>手机：{detail.contact.phone ?? '-'}</span>
                        {detail.contact.whatsapp && <span>WhatsApp：{detail.contact.whatsapp}</span>}
                        {detail.contact.altPhone && <span>备用：{detail.contact.altPhone}</span>}
                        <span>地址：{detail.contact.address ?? '-'}</span>
                      </Space>
                    </Card>
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
                      form={ptpForm}
                      layout="vertical"
                      onFinish={handleAddPTP}
                    >
                      <Form.Item label="承诺金额 (GHS)" name="amount" rules={[{ required: true }]}>
                        <InputNumber style={{ width: '100%' }} min={0} />
                      </Form.Item>
                      <Form.Item label="承诺日期" name="promiseDate" rules={[{ required: true }]}>
                        <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
                      </Form.Item>
                      <Form.Item label="更新案件状态" name="status" initialValue="PROMISE">
                        <Select options={CASE_STATUS_OPTIONS} placeholder="选择状态（可选）" allowClear />
                      </Form.Item>
                      <Form.Item label="备注" name="note">
                        <Input.TextArea rows={2} />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block loading={ptpMutation.isPending}>
                        新增承诺
                      </Button>
                    </Form>
                    <List
                      dataSource={detail.ptpRecords ?? []}
                      locale={{ emptyText: '暂无 PTP 记录' }}
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
                    dataSource={detail.callLogs ?? []}
                    locale={{ emptyText: '暂无外呼记录' }}
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
                  <Form layout="vertical" onFinish={handleAddFollowUp} form={followForm}>
                    <Form.Item label="跟进行为" name="action" rules={[{ required: true }]}>
                      <Input.TextArea rows={3} placeholder="如：外呼 / 短信 / 上门" />
                    </Form.Item>
                    <Form.Item label="结果" name="result" rules={[{ required: true }]}>
                      <Input.TextArea rows={3} placeholder="如：客户承诺、无人接听" />
                    </Form.Item>
                    <Form.Item label="更新状态" name="status">
                      <Select options={CASE_STATUS_OPTIONS} placeholder="选择新的案件状态（可选）" allowClear />
                    </Form.Item>
                    <Form.Item label="备注" name="note">
                      <Input.TextArea rows={2} placeholder="可填写补充说明" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block loading={followUpMutation.isPending}>
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
