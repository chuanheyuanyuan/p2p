import { Card, Form, Input, Select, Space, Table, Tag, type TableColumnsType } from 'antd';
import { collectionCasesMock, type CollectionCase } from '../mocks/data';

const Collections = () => {
  const columns: TableColumnsType<CollectionCase> = [
    { title: '案件号', dataIndex: 'caseId' },
    { title: '借款人', dataIndex: 'user' },
    { title: 'Bucket', dataIndex: 'bucket' },
    { title: '逾期金额', dataIndex: 'amount' },
    { title: '分案团队', dataIndex: 'assignee' },
    { title: '到期日', dataIndex: 'due' },
    { title: '状态', dataIndex: 'status', render: (value) => <Tag color="blue">{value}</Tag> }
  ];

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Form layout="vertical" className="form-grid">
          <Form.Item label="案件号" name="caseId">
            <Input placeholder="输入案件号" allowClear />
          </Form.Item>
          <Form.Item label="Bucket" name="bucket">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'D0', label: 'D0' }, { value: 'D7', label: 'D7' }]} />
          </Form.Item>
          <Form.Item label="催收员" name="assignee">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'team-a', label: 'Team A' }, { value: 'team-b', label: 'Team B' }]} />
          </Form.Item>
          <Form.Item label="承诺状态" name="ptp">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'ptp', label: 'PTP' }, { value: 'broken', label: '坏账' }]} />
          </Form.Item>
        </Form>
      </Card>
      <Card>
        <Table<CollectionCase>
          rowKey="caseId"
          columns={columns}
          dataSource={collectionCasesMock}
          pagination={false}
        />
      </Card>
    </Space>
  );
};

export default Collections;
