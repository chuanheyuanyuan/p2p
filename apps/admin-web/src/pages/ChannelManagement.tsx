import { Card, Table } from 'antd';

type ChannelRow = {
  name: string;
  installs: number;
  conversion: string;
  cost: string;
};

const data: ChannelRow[] = [
  { name: 'Facebook Ads', installs: 187, conversion: '4.3%', cost: '₵12,300' },
  { name: 'Google Ads', installs: 121, conversion: '3.8%', cost: '₵9,500' },
  { name: 'Organic', installs: 74, conversion: '6.1%', cost: '₵0' }
];

const ChannelManagement = () => (
  <Card title="渠道连接统计">
    <Table<ChannelRow>
      rowKey="name"
      dataSource={data}
      pagination={false}
      columns={[
        { title: '渠道', dataIndex: 'name' },
        { title: '安装量', dataIndex: 'installs' },
        { title: '转化率', dataIndex: 'conversion' },
        { title: '渠道成本', dataIndex: 'cost' }
      ]}
    />
  </Card>
);

export default ChannelManagement;
