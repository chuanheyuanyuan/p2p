import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRequest } from 'ahooks';
import { Button, Card, Form, Input, Select, Space, Table, Tag, type TableColumnsType } from 'antd';
import type { ApplicationRecord } from '../mocks/data';
import { fetchApplications, type ApplicationQuery } from '../services/api';

const PAGE_SIZE = 5;

const Applications = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [query, setQuery] = useState<ApplicationQuery>({ page: 1, pageSize: PAGE_SIZE });

  const { data, loading } = useRequest(() => fetchApplications(query), {
    refreshDeps: [query]
  });

  const handleSearch = () => {
    const values = form.getFieldsValue();
    setQuery({
      ...query,
      page: 1,
      keyword: values.phone,
      product: values.product,
      level: values.level
    });
  };

  const handleTableChange = (pagination: { current?: number; pageSize?: number }) => {
    setQuery((prev) => ({
      ...prev,
      page: pagination.current,
      pageSize: pagination.pageSize
    }));
  };

  const columns: TableColumnsType<ApplicationRecord> = [
    { title: '贷款编号', dataIndex: 'id', render: (value) => <a onClick={() => navigate(`/applications/${value}`)}>{value}</a> },
    { title: '产品名称', dataIndex: 'product' },
    { title: '用户姓名', dataIndex: 'name', render: (value, record) => <a onClick={() => navigate(`/users/${record.userId}`)}>{value}</a> },
    { title: '申请渠道', dataIndex: 'channel' },
    { title: '用户等级', dataIndex: 'level' },
    { title: '金额', dataIndex: 'amount' },
    { title: '期限', dataIndex: 'term' },
    { title: '审核员', dataIndex: 'reviewer' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: ApplicationRecord['status']) => (
        <Tag color={status === '通过' ? 'green' : 'red'}>{status}</Tag>
      )
    },
    {
      title: '操作',
      dataIndex: 'action',
      render: (_, record) => (
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

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Card>
        <Form layout="vertical" form={form} className="form-grid">
          <Form.Item label="手机号" name="phone">
            <Input placeholder="请输入" allowClear />
          </Form.Item>
          <Form.Item label="申请时间" name="time">
            <Input placeholder="2025-07-19 ~ 2025-10-20" />
          </Form.Item>
          <Form.Item label="贷款类型" name="product">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'max', label: 'InsCash Max' }]} allowClear />
          </Form.Item>
          <Form.Item label="用户等级" name="level">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'level5', label: 'Level5' }]} allowClear />
          </Form.Item>
          <Form.Item label="申请渠道" name="channel">
            <Select options={[{ value: 'all', label: '全部' }, { value: 'facebook', label: 'Facebook Ads' }, { value: 'google', label: 'Google Ads' }]} allowClear />
          </Form.Item>
          <Form.Item label="App 版本" name="app">
            <Select options={[{ value: 'all', label: '全部' }, { value: '1.0.17', label: '1.0.17' }]} allowClear />
          </Form.Item>
        </Form>
        <Space style={{ marginTop: 12 }}>
          <Button type="primary" onClick={handleSearch}>
            查询
          </Button>
          <Button onClick={() => form.resetFields()}>重置</Button>
          <Button>导出</Button>
        </Space>
      </Card>
      <Card>
        <Table<ApplicationRecord>
          rowKey="id"
          columns={columns}
          dataSource={data?.list ?? []}
          loading={loading}
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
