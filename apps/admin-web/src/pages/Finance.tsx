import { type ReactNode, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  Button,
  Card,
  Col,
  DatePicker,
  Form,
  Input,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tabs,
  Tag,
  Typography,
  message
} from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import type { FinanceDisbursement, FinanceRepayment, ReconciliationDiff } from '../mocks/data';
import {
  exportReconciliation,
  fetchFinanceDisbursements,
  fetchFinanceRepayments,
  fetchReconciliationDiffs,
  retryFinanceDisbursement,
  type FinanceQuery
} from '../services/api';
import { formatCurrency } from '../utils/format';

const { RangePicker } = DatePicker;
const channelOptions = ['Bank Transfer', 'Flutterwave', 'UnionPay', 'USSD'];
const disbursementStatusColors: Record<FinanceDisbursement['status'], string> = {
  待打款: 'blue',
  成功: 'green',
  失败: 'red',
  重试中: 'orange'
};
const repaymentStatusColors: Record<FinanceRepayment['status'], string> = {
  待入账: 'blue',
  成功: 'green',
  失败: 'red',
  异常: 'orange'
};
const diffStatusColors: Record<ReconciliationDiff['status'], string> = {
  未处理: 'red',
  处理中: 'orange',
  已解决: 'green'
};

const formatRange = (range?: [Dayjs, Dayjs]) => ({
  startDate: range?.[0]?.format('YYYY-MM-DD'),
  endDate: range?.[1]?.format('YYYY-MM-DD')
});

const disbursementStatusOptions = [
  { label: '待打款', value: '待打款' },
  { label: '成功', value: '成功' },
  { label: '失败', value: '失败' },
  { label: '重试中', value: '重试中' }
];

const repaymentStatusOptions = [
  { label: '待入账', value: '待入账' },
  { label: '成功', value: '成功' },
  { label: '失败', value: '失败' },
  { label: '异常', value: '异常' }
];

const diffStatusOptions = [
  { label: '未处理', value: '未处理' },
  { label: '处理中', value: '处理中' },
  { label: '已解决', value: '已解决' }
];

const Finance = () => {
  const [activeTab, setActiveTab] = useState('disbursement');
  const [disburseFilters, setDisburseFilters] = useState<FinanceQuery>(() => formatRange([dayjs().subtract(6, 'day'), dayjs()]));
  const [repaymentFilters, setRepaymentFilters] = useState<FinanceQuery>(() =>
    formatRange([dayjs().subtract(6, 'day'), dayjs()])
  );
  const [diffFilters, setDiffFilters] = useState<FinanceQuery>(() => formatRange([dayjs().subtract(6, 'day'), dayjs()]));
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const {
    data: disbursementData,
    isPending: disbursementLoading,
    error: disbursementError
  } = useQuery({
    queryKey: ['finance-disbursements', disburseFilters],
    queryFn: () => fetchFinanceDisbursements(disburseFilters),
    enabled: activeTab === 'disbursement'
  });

  const {
    data: repaymentData,
    isPending: repaymentLoading,
    error: repaymentError
  } = useQuery({
    queryKey: ['finance-repayments', repaymentFilters],
    queryFn: () => fetchFinanceRepayments(repaymentFilters),
    enabled: activeTab === 'repayment'
  });

  const {
    data: diffData,
    isPending: diffLoading,
    error: diffError
  } = useQuery({
    queryKey: ['finance-diff', diffFilters],
    queryFn: () => fetchReconciliationDiffs(diffFilters),
    enabled: activeTab === 'reconciliation'
  });

  const retryMutation = useMutation({
    mutationFn: retryFinanceDisbursement,
    onSuccess: () => {
      message.success('已触发通道重试');
      queryClient.invalidateQueries({ queryKey: ['finance-disbursements'] });
    },
    onError: (error: Error) => {
      message.error(error.message);
    }
  });

  const disbursementSummary = useMemo(() => {
    const list = disbursementData?.list ?? [];
    const totalAmount = list.reduce((sum, item) => sum + item.amount, 0);
    const failed = list.filter((item) => item.status === '失败').length;
    return { totalAmount, failed, count: list.length };
  }, [disbursementData]);

  const repaymentSummary = useMemo(() => {
    const list = repaymentData?.list ?? [];
    const totalAmount = list.reduce((sum, item) => sum + item.amount, 0);
    const pending = list.filter((item) => item.status === '待入账').length;
    return { totalAmount, pending, count: list.length };
  }, [repaymentData]);

  const disbursementColumns: ColumnsType<FinanceDisbursement> = [
    {
      title: 'Loan ID',
      dataIndex: 'loanId',
      render: (value) => (
        <Typography.Link onClick={() => navigate(`/applications/${value}`)}>{value}</Typography.Link>
      )
    },
    { title: '借款人', dataIndex: 'user' },
    {
      title: '金额',
      dataIndex: 'amount',
      render: (value, record) => formatCurrency(value, record.currency === 'GHS' ? '₵' : record.currency)
    },
    { title: '渠道', dataIndex: 'channel' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: FinanceDisbursement['status']) => <Tag color={disbursementStatusColors[status]}>{status}</Tag>
    },
    { title: '失败原因', dataIndex: 'failureReason', render: (value) => value ?? '-' },
    { title: '请求时间', dataIndex: 'requestedAt' },
    { title: '更新时间', dataIndex: 'updatedAt' },
    {
      title: '操作',
      render: (_, record) =>
        record.status === '失败' ? (
          <Button type="link" onClick={() => retryMutation.mutate(record.id)} loading={retryMutation.isPending}>
            重试
          </Button>
        ) : (
          '-'
        )
    }
  ];

  const repaymentColumns: ColumnsType<FinanceRepayment> = [
    { title: 'Repayment ID', dataIndex: 'repaymentId' },
    { title: 'Loan ID', dataIndex: 'loanId' },
    { title: '借款人', dataIndex: 'user' },
    {
      title: '金额',
      dataIndex: 'amount',
      render: (value, record) => formatCurrency(value, record.currency === 'GHS' ? '₵' : record.currency)
    },
    { title: '渠道', dataIndex: 'channel' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: FinanceRepayment['status']) => <Tag color={repaymentStatusColors[status]}>{status}</Tag>
    },
    { title: '支付时间', dataIndex: 'paidAt' },
    { title: '入账时间', dataIndex: 'recordedAt' },
    {
      title: '差异',
      dataIndex: 'difference',
      render: (value?: number) =>
        value && value !== 0 ? <Tag color={value > 0 ? 'green' : 'red'}>{value.toFixed(2)}</Tag> : '-'
    }
  ];

  const diffColumns: ColumnsType<ReconciliationDiff> = [
    { title: '日期', dataIndex: 'date' },
    { title: '类型', dataIndex: 'type' },
    { title: '渠道', dataIndex: 'channel' },
    {
      title: '通道金额',
      dataIndex: 'channelAmount',
      render: (value, record) => formatCurrency(value, record.currency === 'GHS' ? '₵' : record.currency)
    },
    {
      title: 'Ledger 金额',
      dataIndex: 'ledgerAmount',
      render: (value, record) => formatCurrency(value, record.currency === 'GHS' ? '₵' : record.currency)
    },
    {
      title: '差异',
      render: (_, record) => {
        const diff = record.channelAmount - record.ledgerAmount;
        return <Tag color={diff === 0 ? 'green' : diff > 0 ? 'orange' : 'red'}>{diff.toFixed(2)}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: ReconciliationDiff['status']) => <Tag color={diffStatusColors[status]}>{status}</Tag>
    },
    { title: '备注', dataIndex: 'note', render: (value) => value ?? '-' }
  ];

  const handleDisbursementSearch = (values: { status?: string; channel?: string; keyword?: string; range?: Dayjs[] }) => {
    const rangeValues = Array.isArray(values.range) ? (values.range as [Dayjs, Dayjs]) : undefined;
    setDisburseFilters({
      status: values.status || undefined,
      channel: values.channel || undefined,
      keyword: values.keyword?.trim() || undefined,
      ...formatRange(rangeValues)
    });
  };

  const handleRepaymentSearch = (values: { status?: string; channel?: string; keyword?: string; range?: Dayjs[] }) => {
    const rangeValues = Array.isArray(values.range) ? (values.range as [Dayjs, Dayjs]) : undefined;
    setRepaymentFilters({
      status: values.status || undefined,
      channel: values.channel || undefined,
      keyword: values.keyword?.trim() || undefined,
      ...formatRange(rangeValues)
    });
  };

  const handleDiffSearch = (values: { status?: string; channel?: string; type?: string; range?: Dayjs[] }) => {
    const rangeValues = Array.isArray(values.range) ? (values.range as [Dayjs, Dayjs]) : undefined;
    setDiffFilters({
      status: values.status || undefined,
      channel: values.channel || undefined,
      type: values.type || undefined,
      ...formatRange(rangeValues)
    });
  };

  const handleExportDiff = async () => {
    try {
      const { taskId } = await exportReconciliation(diffFilters);
      message.success(`已创建对账导出任务：${taskId}`);
    } catch (error) {
      message.error((error as Error).message);
    }
  };

  const renderFilterForm = (
    formKey: string,
    onFinish: (values: any) => void,
    options?: {
      initialRange?: [Dayjs, Dayjs];
      statusOptions?: { label: string; value: string }[];
      showKeyword?: boolean;
      extraFields?: ReactNode;
    }
  ) => {
    const { initialRange = [dayjs().subtract(6, 'day'), dayjs()], statusOptions, showKeyword = true, extraFields } =
      options ?? {};
    return (
      <Form
        layout="inline"
        onFinish={onFinish}
        onReset={() => onFinish({})}
        initialValues={{ range: initialRange }}
        key={formKey}
      >
        {statusOptions && (
          <Form.Item name="status" label="状态">
            <Select allowClear placeholder="全部">
              {statusOptions.map((option) => (
                <Select.Option key={option.value} value={option.value}>
                  {option.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        )}
        <Form.Item name="channel" label="渠道">
          <Select allowClear placeholder="全部">
            {channelOptions.map((option) => (
              <Select.Option value={option} key={option}>
                {option}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>
        {extraFields}
        <Form.Item name="range" label="日期范围">
          <RangePicker allowClear />
        </Form.Item>
        {showKeyword && (
          <Form.Item name="keyword" label="关键词">
            <Input placeholder="Loan ID / 用户" allowClear />
          </Form.Item>
        )}
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              查询
            </Button>
            <Button htmlType="reset">
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    );
  };

  return (
    <Tabs
      activeKey={activeTab}
      onChange={setActiveTab}
      items={[
        {
          key: 'disbursement',
          label: '放款管理',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
              {disbursementError && (
                <Alert type="error" message="放款数据加载失败" description={(disbursementError as Error).message} />
              )}
              <Row gutter={16}>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="总放款金额（筛选）"
                      value={formatCurrency(disbursementSummary.totalAmount, '₵')}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic title="记录数" value={disbursementSummary.count} />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic title="失败笔数" value={disbursementSummary.failed} valueStyle={{ color: '#cf1322' }} />
                  </Card>
                </Col>
              </Row>
              {renderFilterForm('disbursement-filter', handleDisbursementSearch, {
                statusOptions: disbursementStatusOptions
              })}
              <Table
                rowKey="id"
                columns={disbursementColumns}
                dataSource={disbursementData?.list ?? []}
                loading={disbursementLoading}
                pagination={false}
              />
            </Space>
          )
        },
        {
          key: 'repayment',
          label: '还款管理',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
              {repaymentError && (
                <Alert type="error" message="还款数据加载失败" description={(repaymentError as Error).message} />
              )}
              <Row gutter={16}>
                <Col span={8}>
                  <Card>
                    <Statistic title="总还款金额（筛选）" value={formatCurrency(repaymentSummary.totalAmount, '₵')} />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic title="记录数" value={repaymentSummary.count} />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic title="待入账" value={repaymentSummary.pending} valueStyle={{ color: '#faad14' }} />
                  </Card>
                </Col>
              </Row>
              {renderFilterForm('repayment-filter', handleRepaymentSearch, {
                statusOptions: repaymentStatusOptions
              })}
              <Table
                rowKey="repaymentId"
                columns={repaymentColumns}
                dataSource={repaymentData?.list ?? []}
                loading={repaymentLoading}
                pagination={false}
              />
            </Space>
          )
        },
        {
          key: 'reconciliation',
          label: '对账差异',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
              {diffError && <Alert type="error" message="对账数据加载失败" description={(diffError as Error).message} />}
              {renderFilterForm('diff-filter', handleDiffSearch, {
                statusOptions: diffStatusOptions,
                showKeyword: false,
                extraFields: (
                  <Form.Item name="type" label="类型">
                    <Select allowClear placeholder="全部">
                      <Select.Option value="放款">放款</Select.Option>
                      <Select.Option value="还款">还款</Select.Option>
                    </Select>
                  </Form.Item>
                )
              })}
              <Button type="primary" onClick={handleExportDiff} style={{ alignSelf: 'flex-end' }}>
                导出差异
              </Button>
              <Table
                rowKey="id"
                columns={diffColumns}
                dataSource={diffData?.list ?? []}
                loading={diffLoading}
                pagination={false}
              />
            </Space>
          )
        }
      ]}
    />
  );
};

export default Finance;
