import { Button, Card, DatePicker, Form, Select, Space, Table, type TableColumnsType } from 'antd';
import dayjs from 'dayjs';
import { dailyStatsMock, type DailyStat } from '../mocks/data';

const DailyStats = () => {
  const [form] = Form.useForm();

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

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Form
          layout="vertical"
          form={form}
          initialValues={{
            daterange: [dayjs('2025-10-11'), dayjs('2025-10-20')],
            channel: 'all',
            repeat: 'all'
          }}
        >
          <div className="form-grid">
            <Form.Item label="时间范围" name="daterange">
              <DatePicker.RangePicker allowClear={false} />
            </Form.Item>
            <Form.Item label="是否复借" name="repeat">
              <Select options={[{ value: 'all', label: '全部' }, { value: 'yes', label: '是' }, { value: 'no', label: '否' }]} />
            </Form.Item>
            <Form.Item label="渠道" name="channel">
              <Select options={[{ value: 'all', label: '全部渠道' }, { value: 'facebook', label: 'Facebook' }, { value: 'google', label: 'Google' }]} />
            </Form.Item>
          </div>
          <Space>
            <Button type="primary">查询</Button>
            <Button htmlType="reset">重置</Button>
          </Space>
        </Form>
      </Card>
      <Card>
        <Table<DailyStat>
          rowKey="date"
          columns={columns}
          dataSource={dailyStatsMock}
          pagination={{ pageSize: 5 }}
        />
      </Card>
    </Space>
  );
};

export default DailyStats;
