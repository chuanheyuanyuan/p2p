import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, Card, DatePicker, Form, Input, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { TableColumnsType, TableProps } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query';
import type { ApplicationRecord } from '../mocks/data';
import { exportApplications, fetchApplications, type ApplicationQuery } from '../services/api';
import { formatCurrency, maskPhone } from '../utils/format';
import { useApplicationFilterStore } from '../store/applicationFilters';

const { RangePicker } = DatePicker;
const PAGE_SIZE = 10;
const STATUS_OPTIONS = [
  { value: '通过', label: '通过' },
  { value: '审核中', label: '审核中' },
  { value: '待签署', label: '待签署' },
  { value: '拒绝', label: '拒绝' }
];
const statusColorMap: Record<string, string> = {
  通过: 'green',
  审核中: 'gold',
  待签署: 'blue',
  拒绝: 'red'
};

const Applications = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const filterStore = useApplicationFilterStore();
  const { setFilters, reset, ...query } = filterStore;
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  const { data, isPending, isFetching, error } = useQuery({
    queryKey: ['applications', query],
    queryFn: () => fetchApplications(query),
    placeholderData: keepPreviousData,
    staleTime: 30 * 1000
  });

  const exportMutation = useMutation({
    mutationFn: () => exportApplications(query),
    onSuccess: (result) => {
      message.success(`导出任务已创建：${result.taskId}`);
    },
    onError: (err) => {
      message.error(err instanceof Error ? err.message : '导出失败，请稍后再试');
    }
  });

  const handleSearch = () => {
    const values = form.getFieldsValue();
    const range = values.daterange as [Dayjs, Dayjs] | undefined;
    setFilters({
      ...query,
      page: 1,
      loanId: values.loanId || undefined,
      keyword: values.keyword || undefined,
      phone: values.phone || undefined,
      status: values.status || undefined,
      product: values.product || undefined,
      channel: values.channel || undefined,
      level: values.level || undefined,
      appVersion: values.appVersion || undefined,
      reviewer: values.reviewer || undefined,
      repeat: values.repeat || undefined,
      startDate: range?.[0]?.format('YYYY-MM-DD') ?? undefined,
      endDate: range?.[1]?.format('YYYY-MM-DD') ?? undefined,
      pageSize: query.pageSize
    });
    setSelectedRowKeys([]);
  };

  const handleReset = () => {
    reset();
    form.resetFields();
    setSelectedRowKeys([]);
  };

  const handleTableChange = (pagination: { current?: number; pageSize?: number }) => {
    setFilters({
      ...query,
      page: pagination.current ?? query.page,
      pageSize: pagination.pageSize ?? query.pageSize
    });
    setSelectedRowKeys([]);
  };

  const columns: TableColumnsType<ApplicationRecord> = useMemo(() => {
    return [
      {
        title: '贷款编号',
        dataIndex: 'id',
        render: (value: string) => (
          <Typography.Link onClick={() => navigate(`/applications/${value}`)}>{value}</Typography.Link>
        )
      },
      { title: '产品', dataIndex: 'product' },
      {
        title: '借款人',
        render: (_: unknown, record: ApplicationRecord) => (
          <Space direction="vertical" size={0}>
            <Button type="link" onClick={() => navigate(`/users/${record.userId}`)} style={{ padding: 0 }}>
              {record.name}
            </Button>
            <Typography.Text type="secondary">{maskPhone(record.phone)}</Typography.Text>
            <Space size={4} wrap>
              {record.repeat && <Tag color="purple">复借</Tag>}
              {record.tags?.map((tag) => (
                <Tag key={`${record.id}-${tag}`}>{tag}</Tag>
              ))}
            </Space>
          </Space>
        )
      },
      { title: '渠道', dataIndex: 'channel' },
      { title: '等级', dataIndex: 'level' },
      {
        title: '金额',
        dataIndex: 'amount',
        render: (value: number) => formatCurrency(value)
      },
      { title: '期限', dataIndex: 'term' },
      {
        title: '剩余本金',
        dataIndex: 'outstandingAmount',
        render: (value?: number) => (value ? formatCurrency(value) : '-')
      },
      {
        title: '风险分',
        dataIndex: 'riskScore',
        render: (value?: number) => (value ? value : '-')
      },
      {
        title: '状态',
        dataIndex: 'status',
        render: (value: ApplicationRecord['status']) => (
          <Tag color={statusColorMap[value] ?? 'default'}>{value}</Tag>
        )
      },
      { title: '审核员', dataIndex: 'reviewer' },
      { title: 'App 版本', dataIndex: 'appVersion' },
      {
        title: '上次还款',
        dataIndex: 'lastPaidAt',
        render: (value?: string) => value ?? '-'
      },
      { title: '提交时间', dataIndex: 'submittedAt' },
      {
        title: '操作',
        render: (_: unknown, record: ApplicationRecord) => (
          <Space>
            <Button type="link" onClick={() => navigate(`/applications/${record.id}`)}>
              查看详情
            </Button>
            <Button type="link" onClick={() => navigate(`/users/${record.userId}`)}>
              用户档案
            </Button>
          </Space>
        )
      }
    ];
  }, [navigate]);

  const formInitialValues = useMemo(() => {
    const range = query.startDate && query.endDate ? [dayjs(query.startDate), dayjs(query.endDate)] : undefined;
    return { ...query, daterange: range };
  }, [query]);

  useEffect(() => {
    form.setFieldsValue(formInitialValues);
  }, [form, formInitialValues]);

  const handleBatchExport = () => {
    message.info(`已触发 ${selectedRowKeys.length} 条申请的批量导出`);
  };

  const handleBatchReview = () => {
    message.success(`已提交 ${selectedRowKeys.length} 条申请的复核任务`);
    setSelectedRowKeys([]);
  };

  const rowSelection: TableProps<ApplicationRecord>['rowSelection'] = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys as string[])
  };

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Form layout="vertical" form={form} className="form-grid" initialValues={formInitialValues}>
          <Form.Item label="贷款编号" name="loanId">
            <Input placeholder="LN2025..." allowClear />
          </Form.Item>
          <Form.Item label="关键字" name="keyword">
            <Input placeholder="借款人/贷款号" allowClear />
          </Form.Item>
          <Form.Item label="关键字" name="keyword">
            <Input placeholder="借款人/loanId" allowClear />
          </Form.Item>
          <Form.Item label="手机号" name="phone">
            <Input placeholder="+233..." allowClear />
          </Form.Item>
          <Form.Item label="申请时间" name="daterange">
            <RangePicker allowClear style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="审核状态" name="status">
            <Select options={STATUS_OPTIONS} allowClear placeholder="全部" />
          </Form.Item>
          <Form.Item label="申请渠道" name="channel">
            <Select
              allowClear
              placeholder="全部"
              options={[
                { value: 'Google Ads', label: 'Google Ads' },
                { value: 'Facebook Ads', label: 'Facebook Ads' },
                { value: 'Affiliate', label: 'Affiliate' }
              ]}
            />
          </Form.Item>
          <Form.Item label="产品" name="product">
            <Select
              allowClear
              placeholder="全部"
              options={[
                { value: 'InsCash Plus', label: 'InsCash Plus' },
                { value: 'InsCash Max', label: 'InsCash Max' },
                { value: 'InsCash Pro', label: 'InsCash Pro' }
              ]}
            />
          </Form.Item>
          <Form.Item label="用户等级" name="level">
            <Select
              allowClear
              placeholder="全部"
              options={['Level5', 'Level4', 'Level3', 'Level2', 'Level1'].map((level) => ({
                value: level,
                label: level
              }))}
            />
          </Form.Item>
          <Form.Item label="App 版本" name="appVersion">
            <Select allowClear placeholder="全部" options={['1.0.17', '1.0.16', '1.0.15'].map((v) => ({ value: v, label: v }))} />
          </Form.Item>
          <Form.Item label="审核员" name="reviewer">
            <Input placeholder="审批员姓名" allowClear />
          </Form.Item>
          <Form.Item label="是否复借" name="repeat">
            <Select
              allowClear
              placeholder="全部"
              options={[
                { value: 'yes', label: '是' },
                { value: 'no', label: '否' }
              ]}
            />
          </Form.Item>
        </Form>
        <Space style={{ marginTop: 12 }}>
          <Button type="primary" onClick={handleSearch}>
            查询
          </Button>
          <Button onClick={handleReset}>重置</Button>
          <Button icon={<DownloadOutlined />} loading={exportMutation.isPending} onClick={() => exportMutation.mutate()}>
            导出
          </Button>
        </Space>
      </Card>

      {error && (
        <Alert
          type="error"
          message="申请列表加载失败"
          description={(error as Error).message}
          action={
            <Button size="small" onClick={handleSearch}>
              重试
            </Button>
          }
        />
      )}

      {selectedRowKeys.length > 0 && (
        <Card>
          <Space size={16}>
            <Typography.Text>已选 {selectedRowKeys.length} 条申请</Typography.Text>
            <Button size="small" onClick={handleBatchExport}>
              批量导出
            </Button>
            <Button size="small" type="primary" onClick={handleBatchReview}>
              批量复核
            </Button>
          </Space>
        </Card>
      )}

      <Card>
        <Table<ApplicationRecord>
          rowKey="id"
          columns={columns}
          dataSource={data?.list ?? []}
          loading={isPending || isFetching}
          rowSelection={rowSelection}
          pagination={{
            current: query.page,
            pageSize: query.pageSize,
            total: data?.total
          }}
          onChange={handleTableChange}
        />
      </Card>
    </Space>
  );
};

export default Applications;
