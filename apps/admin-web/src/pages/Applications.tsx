import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, Card, DatePicker, Form, Input, Select, Space, Table, Tag, Typography, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query';
import type { ApplicationRecord } from '../mocks/data';
import { exportApplications, fetchApplications, type ApplicationQuery } from '../services/api';
import { formatCurrency, maskPhone } from '../utils/format';

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
  const [query, setQuery] = useState<ApplicationQuery>({ page: 1, pageSize: PAGE_SIZE });

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
    setQuery((prev) => ({
      ...prev,
      page: 1,
      loanId: values.loanId || undefined,
      phone: values.phone || undefined,
      status: values.status || undefined,
      product: values.product || undefined,
      channel: values.channel || undefined,
      level: values.level || undefined,
      appVersion: values.appVersion || undefined,
      reviewer: values.reviewer || undefined,
      repeat: values.repeat || undefined,
      startDate: range?.[0]?.format('YYYY-MM-DD'),
      endDate: range?.[1]?.format('YYYY-MM-DD')
    }));
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({ page: 1, pageSize: PAGE_SIZE });
  };

  const handleTableChange = (pagination: { current?: number; pageSize?: number }) => {
    setQuery((prev) => ({
      ...prev,
      page: pagination.current,
      pageSize: pagination.pageSize
    }));
  };

  const columns = useMemo(() => {
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
        title: '状态',
        dataIndex: 'status',
        render: (value: ApplicationRecord['status']) => (
          <Tag color={statusColorMap[value] ?? 'default'}>{value}</Tag>
        )
      },
      { title: '审核员', dataIndex: 'reviewer' },
      { title: 'App 版本', dataIndex: 'appVersion' },
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

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Form
          layout="vertical"
          form={form}
          className="form-grid"
          initialValues={{
            daterange: [dayjs().subtract(7, 'day'), dayjs()],
            repeat: undefined
          }}
        >
          <Form.Item label="贷款编号" name="loanId">
            <Input placeholder="LN2025..." allowClear />
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

      <Card>
        <Table<ApplicationRecord>
          rowKey="id"
          columns={columns}
          dataSource={data?.list ?? []}
          loading={isPending || isFetching}
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
