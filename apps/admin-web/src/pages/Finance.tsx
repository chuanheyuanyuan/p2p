import { useState, useMemo } from 'react';
import { Alert, Button, Card, DatePicker, Form, Input, Select, Space, Table, Tabs, Tag, message } from 'antd';
import type { TableColumnsType } from 'antd';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { DisbursementRecord, RepaymentRecord, ReconciliationRecord } from '../mocks/data';
import { fetchDisbursements, fetchReconciliations, fetchRepayments, type FinanceQuery } from '../services/api';
import { formatCurrency } from '../utils/format';

const { RangePicker } = DatePicker;

const initialRange: [Dayjs, Dayjs] = [dayjs().subtract(7, 'day'), dayjs()];

const buildRangeValues = (range?: [Dayjs, Dayjs]) => ({
  startDate: range?.[0]?.format('YYYY-MM-DD'),
  endDate: range?.[1]?.format('YYYY-MM-DD')
});

const Finance = () => {
  return (
    <Tabs
      defaultActiveKey="disbursements"
      items={[
        { key: 'disbursements', label: '放款明细', children: <DisbursementTable /> },
        { key: 'repayments', label: '还款明细', children: <RepaymentTable /> },
        { key: 'reconciliations', label: '对账记录', children: <ReconciliationTable /> }
      ]}
    />
  );
};

const DisbursementTable = () => {
  const [form] = Form.useForm();
  const [query, setQuery] = useState<FinanceQuery>(() => ({ page: 1, pageSize: 10, ...buildRangeValues(initialRange) }));

  const { data, isPending, isFetching, error, refetch } = useQuery({
    queryKey: ['finance-disbursements', query],
    queryFn: () => fetchDisbursements(query),
    placeholderData: keepPreviousData,
    staleTime: 60 * 1000
  });

  const columns: TableColumnsType<DisbursementRecord> = useMemo(
    () => [
      { title: '请求号', dataIndex: 'reqNo' },
      { title: '贷款号', dataIndex: 'loanId' },
      {
        title: '金额',
        dataIndex: 'amount',
        render: (value: number) => formatCurrency(value)
      },
      { title: '渠道', dataIndex: 'channel' },
      {
        title: '状态',
        dataIndex: 'status',
        render: (value: string, record) => <Tag color={value === 'SUCCESS' ? 'green' : value === 'FAILED' ? 'red' : 'blue'}>{record.status}</Tag>
      },
      { title: '失败原因', dataIndex: 'failureReason', render: (value?: string) => value ?? '-' },
      { title: '发起时间', dataIndex: 'createdAt' }
    ],
    []
  );

  const handleSearch = () => {
    const values = form.getFieldsValue();
    const range = values.daterange as [dayjs.Dayjs, dayjs.Dayjs] | undefined;
    setQuery({
      ...query,
      page: 1,
      status: values.status || undefined,
      channel: values.channel || undefined,
      loanId: values.loanId || undefined,
      ...buildRangeValues(range)
    });
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({ page: 1, pageSize: 10, ...buildRangeValues(initialRange) });
  };

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card>
        <Form
          layout="inline"
          form={form}
          initialValues={{
            daterange: initialRange,
            status: undefined,
            channel: undefined
          }}
        >
          <Form.Item label="状态" name="status">
            <Select allowClear style={{ width: 160 }} options={['SUCCESS', 'FAILED', 'PENDING'].map((s) => ({ value: s, label: s }))} />
          </Form.Item>
          <Form.Item label="渠道" name="channel">
            <Input placeholder="mock-channel" allowClear style={{ width: 160 }} />
          </Form.Item>
          <Form.Item label="贷款号" name="loanId">
            <Input placeholder="LN..." allowClear style={{ width: 180 }} />
          </Form.Item>
          <Form.Item label="创建时间" name="daterange">
            <RangePicker />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleSearch}>
                查询
              </Button>
              <Button onClick={handleReset}>重置</Button>
              <Button onClick={() => message.info('已触发导出任务')}>
                导出
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
      {error && <Alert type="error" message="拉取放款失败" action={<Button onClick={() => refetch()}>重试</Button>} />}
      <Card>
        <Table<DisbursementRecord>
          rowKey="reqNo"
          columns={columns}
          dataSource={data?.list}
          loading={isPending || isFetching}
          pagination={{
            current: query.page,
            pageSize: query.pageSize,
            total: data?.total,
            onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
          }}
        />
      </Card>
    </Space>
  );
};

const RepaymentTable = () => {
  const [form] = Form.useForm();
  const [query, setQuery] = useState<FinanceQuery>(() => ({ page: 1, pageSize: 10, ...buildRangeValues(initialRange) }));
  const { data, isPending, isFetching, error, refetch } = useQuery({
    queryKey: ['finance-repayments', query],
    queryFn: () => fetchRepayments(query),
    placeholderData: keepPreviousData,
    staleTime: 60 * 1000
  });

  const columns: TableColumnsType<RepaymentRecord> = useMemo(
    () => [
      { title: '还款号', dataIndex: 'repaymentId' },
      { title: '贷款号', dataIndex: 'loanId' },
      { title: '金额', dataIndex: 'amount', render: (value: number) => formatCurrency(value) },
      { title: '渠道', dataIndex: 'channel' },
      { title: '状态', dataIndex: 'status' },
      { title: 'TXN Ref', dataIndex: 'txnRef' },
      { title: '已入账', dataIndex: 'appliedAmount', render: (value: number) => formatCurrency(value) },
      { title: '剩余应还', dataIndex: 'remainingDue', render: (value: number) => formatCurrency(value) },
      { title: '支付时间', dataIndex: 'paidAt' }
    ],
    []
  );

  const handleSearch = () => {
    const values = form.getFieldsValue();
    const range = values.daterange as [dayjs.Dayjs, dayjs.Dayjs] | undefined;
    setQuery({
      ...query,
      page: 1,
      status: values.status || undefined,
      channel: values.channel || undefined,
      loanId: values.loanId || undefined,
      ...buildRangeValues(range)
    });
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({ page: 1, pageSize: 10, ...buildRangeValues(initialRange) });
  };

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card>
        <Form layout="inline" form={form} initialValues={{ daterange: initialRange }}>
          <Form.Item label="状态" name="status">
            <Select allowClear style={{ width: 160 }} options={['POSTED', 'FAILED', 'PENDING'].map((s) => ({ value: s, label: s }))} />
          </Form.Item>
          <Form.Item label="渠道" name="channel">
            <Input placeholder="MOMO" allowClear style={{ width: 160 }} />
          </Form.Item>
          <Form.Item label="贷款号" name="loanId">
            <Input placeholder="LN..." allowClear style={{ width: 180 }} />
          </Form.Item>
          <Form.Item label="支付时间" name="daterange">
            <RangePicker />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleSearch}>
                查询
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
      {error && <Alert type="error" message="拉取还款失败" action={<Button onClick={() => refetch()}>重试</Button>} />}
      <Card>
        <Table<RepaymentRecord>
          rowKey="repaymentId"
          columns={columns}
          dataSource={data?.list}
          loading={isPending || isFetching}
          pagination={{
            current: query.page,
            pageSize: query.pageSize,
            total: data?.total,
            onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
          }}
        />
      </Card>
    </Space>
  );
};

const ReconciliationTable = () => {
  const [form] = Form.useForm();
  const [query, setQuery] = useState<{ refType?: string; refId?: string; page?: number; pageSize?: number }>({ page: 1, pageSize: 10 });
  const { data, isPending, isFetching, error, refetch } = useQuery({
    queryKey: ['finance-reconciliations', query],
    queryFn: () => fetchReconciliations(query),
    placeholderData: keepPreviousData,
    staleTime: 60 * 1000
  });

  const columns: TableColumnsType<ReconciliationRecord> = useMemo(
    () => [
      { title: 'Entry ID', dataIndex: 'entryId' },
      { title: 'Ref Type', dataIndex: 'refType' },
      { title: 'Ref ID', dataIndex: 'refId' },
      { title: '状态', dataIndex: 'status' },
      { title: '分录数量', dataIndex: 'lineCount' },
      { title: '创建时间', dataIndex: 'createdAt' }
    ],
    []
  );

  const handleSearch = () => {
    const values = form.getFieldsValue();
    setQuery({ ...query, page: 1, refType: values.refType || undefined, refId: values.refId || undefined });
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({ page: 1, pageSize: 10 });
  };

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card>
        <Form layout="inline" form={form}>
          <Form.Item label="Ref Type" name="refType">
            <Select allowClear style={{ width: 160 }} options={['DISBURSEMENT', 'REPAYMENT'].map((s) => ({ value: s, label: s }))} />
          </Form.Item>
          <Form.Item label="Ref ID" name="refId">
            <Input placeholder="LN..." allowClear style={{ width: 180 }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleSearch}>
                查询
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
      {error && <Alert type="error" message="拉取对账失败" action={<Button onClick={() => refetch()}>重试</Button>} />}
      <Card>
        <Table<ReconciliationRecord>
          rowKey="entryId"
          columns={columns}
          dataSource={data?.list}
          loading={isPending || isFetching}
          pagination={{
            current: query.page,
            pageSize: query.pageSize,
            total: data?.total,
            onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
          }}
        />
      </Card>
    </Space>
  );
};

export default Finance;
