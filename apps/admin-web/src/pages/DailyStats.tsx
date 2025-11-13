import { useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  DatePicker,
  Form,
  message,
  Select,
  Space,
  Statistic,
  Table,
  Typography,
  type TableColumnsType
} from 'antd';
import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import type { DailyStat } from '../mocks/data';
import { exportDailyStats, fetchDailyStats, type DailyStatsQuery } from '../services/api';
import { summarizeDailyStats } from '../utils/dailyStats';

const { RangePicker } = DatePicker;

const initialRange = [dayjs().subtract(9, 'day'), dayjs()];

const DailyStats = () => {
  const [form] = Form.useForm();
  const [query, setQuery] = useState<DailyStatsQuery>({
    startDate: initialRange[0].format('YYYY-MM-DD'),
    endDate: initialRange[1].format('YYYY-MM-DD'),
    page: 1,
    pageSize: 10
  });

  const { data, isPending, isFetching, error, refetch } = useQuery({
    queryKey: ['daily-stats', query],
    queryFn: () => fetchDailyStats(query),
    placeholderData: keepPreviousData,
    staleTime: 60 * 1000
  });

  const list = data?.list ?? [];

  const summary = useMemo(() => summarizeDailyStats(list), [list]);

  const exportMutation = useMutation({
    mutationFn: () => exportDailyStats(query),
    onSuccess: (result) => message.success(`已创建导出任务：${result.taskId}`),
    onError: (err) => {
      message.error(err instanceof Error ? err.message : '导出失败，请稍后再试');
    }
  });

  const columns: TableColumnsType<DailyStat> = [
    { title: '日期', dataIndex: 'date' },
    { title: '安装量', dataIndex: 'installs' },
    { title: '注册人数', dataIndex: 'regs' },
    { title: '登录人数', dataIndex: 'logins' },
    { title: '申请笔数', dataIndex: 'applies' },
    { title: '放款笔数', dataIndex: 'disburses' },
    { title: '还款笔数', dataIndex: 'repayments' },
    {
      title: '放款金额 (GHS)',
      dataIndex: 'amount',
      render: (value: number) => value.toLocaleString()
    }
  ];

  const handleSearch = () => {
    const values = form.getFieldsValue();
    const range = values.daterange ?? initialRange;
    setQuery({
      ...query,
      page: 1,
      startDate: range[0].format('YYYY-MM-DD'),
      endDate: range[1].format('YYYY-MM-DD'),
      repeat: values.repeat,
      channel: values.channel
    });
  };

  const handleExport = () => {
    exportMutation.mutate();
  };

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      {error && (
        <Alert
          type="error"
          message="日报数据拉取失败"
          description={(error as Error).message}
          action={
            <Button size="small" onClick={() => refetch()} loading={isFetching}>
              重试
            </Button>
          }
        />
      )}
      <Card>
        <Form
          layout="vertical"
          form={form}
          initialValues={{
            daterange: initialRange,
            repeat: 'all',
            channel: 'all'
          }}
        >
          <div className="form-grid">
            <Form.Item label="时间范围" name="daterange">
              <RangePicker allowClear={false} />
            </Form.Item>
            <Form.Item label="是否复借" name="repeat">
              <Select options={[{ value: 'all', label: '全部' }, { value: 'yes', label: '是' }, { value: 'no', label: '否' }]} />
            </Form.Item>
            <Form.Item label="渠道" name="channel">
              <Select options={[{ value: 'all', label: '全部渠道' }, { value: 'facebook', label: 'Facebook' }, { value: 'google', label: 'Google' }]} />
            </Form.Item>
          </div>
          <Space>
            <Button type="primary" onClick={handleSearch}>
              查询
            </Button>
            <Button onClick={() => { form.resetFields(); handleSearch(); }}>重置</Button>
            <Button onClick={handleExport} loading={exportMutation.isPending}>
              导出
            </Button>
          </Space>
        </Form>
      </Card>

      <Card>
        <Space size={24} wrap>
          <Statistic title="期间安装量" value={summary.installs} />
          <Statistic title="期间注册人数" value={summary.regs} />
          <Statistic title="期间申请笔数" value={summary.applies} />
          <Statistic title="期间放款笔数" value={summary.disburses} />
          <Statistic title="期间放款金额" value={`₵${summary.amount.toLocaleString()}`} />
        </Space>
        <Typography.Paragraph type="secondary" style={{ marginTop: 16 }}>
          数据来自 report-svc `/reports/daily`，默认 15 分钟刷新；导出按钮将创建后台任务。
        </Typography.Paragraph>
      </Card>

      <Card>
        <Table<DailyStat>
          rowKey="date"
          columns={columns}
          dataSource={list}
          loading={isPending || isFetching}
          pagination={{
            current: query.page,
            pageSize: query.pageSize,
            total: data?.total,
            onChange: (page, pageSize) => setQuery((prev) => ({ ...prev, page, pageSize }))
          }}
        />
      </Card>
    </Space>
  );
};

export default DailyStats;
