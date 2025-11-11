import { useMemo, useState } from 'react';
import { Button, Card, DatePicker, Form, Select, Space, Statistic, Table, type TableColumnsType } from 'antd';
import { useRequest } from 'ahooks';
import dayjs from 'dayjs';
import type { DailyStat } from '../mocks/data';
import { fetchDailyStats, type DailyStatsQuery } from '../services/api';

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

  const { data, loading } = useRequest(() => fetchDailyStats(query), {
    refreshDeps: [query]
  });

  const list = data?.list ?? [];

  const summary = useMemo(() => {
    return list.reduce(
      (acc, item) => {
        acc.installs += item.installs;
        acc.regs += item.regs;
        acc.applies += item.applies;
        acc.disburses += item.disburses;
        acc.amount += item.amount;
        return acc;
      },
      { installs: 0, regs: 0, applies: 0, disburses: 0, amount: 0 }
    );
  }, [list]);

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

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
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
      </Card>

      <Card>
        <Table<DailyStat>
          rowKey="date"
          columns={columns}
          dataSource={list}
          loading={loading}
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
