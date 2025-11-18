import { useMemo, useState } from 'react';
import { Alert, Button, Card, Col, DatePicker, Form, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd';
import type { TableColumnsType } from 'antd';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import type { ChannelFunnelRow, OverdueMigrationRow, ReborrowRateRow, ReportCenterData } from '../mocks/data';
import { fetchReportCenter, type ReportCenterQuery } from '../services/api';

const channelOptions = [
  { label: '全部渠道', value: 'all' },
  { label: 'Google Ads', value: 'google' },
  { label: 'Facebook Ads', value: 'facebook' },
  { label: 'Affiliate', value: 'affiliate' }
];

const productOptions = [
  { label: '全部产品', value: 'all' },
  { label: 'InsCash Plus', value: 'plus' },
  { label: 'InsCash Max', value: 'max' },
  { label: 'InsCash Express', value: 'express' }
];

const defaultDate = dayjs();

const formatPercent = (value: number) => `${value}%`;
const renderChangeTag = (value: number) => (
  <Tag color={value >= 0 ? 'green' : 'red'}>{value >= 0 ? `+${value}` : value}pp</Tag>
);

const ReportCenter = () => {
  const [form] = Form.useForm();
  const [query, setQuery] = useState<ReportCenterQuery>({
    businessDate: defaultDate.format('YYYY-MM-DD')
  });

  const { data, isPending, isFetching, error, refetch } = useQuery<ReportCenterData>({
    queryKey: ['report-center', query],
    queryFn: () => fetchReportCenter(query),
    placeholderData: keepPreviousData,
    staleTime: 5 * 60 * 1000
  });

  const summaryCards = data?.summary ?? [];
  const overdueData = data?.overdueMigration ?? [];
  const funnelData = data?.channelFunnel ?? [];
  const reborrowData = data?.reborrowRates ?? [];
  const notes = data?.notes ?? [];

  const handleSearch = () => {
    const values = form.getFieldsValue();
    const dateValue = values.businessDate ? dayjs(values.businessDate) : defaultDate;
    setQuery({
      businessDate: dateValue.format('YYYY-MM-DD'),
      channel: values.channel && values.channel !== 'all' ? values.channel : undefined,
      product: values.product && values.product !== 'all' ? values.product : undefined
    });
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({ businessDate: defaultDate.format('YYYY-MM-DD') });
  };

  const overdueColumns: TableColumnsType<OverdueMigrationRow> = useMemo(
    () => [
      { title: '阶段', dataIndex: 'stage' },
      { title: '今日迁移率', dataIndex: 'todayRate', render: (value: number) => formatPercent(value) },
      { title: '昨日迁移率', dataIndex: 'yesterdayRate', render: (value: number) => formatPercent(value) },
      {
        title: '变化 (pp)',
        dataIndex: 'change',
        render: (value: number) => renderChangeTag(value)
      },
      { title: '备注', dataIndex: 'note' }
    ],
    []
  );

  const channelColumns: TableColumnsType<ChannelFunnelRow> = useMemo(
    () => [
      { title: '渠道', dataIndex: 'channel' },
      { title: '安装量', dataIndex: 'installs', render: (value: number) => value.toLocaleString() },
      { title: '注册人数', dataIndex: 'regs', render: (value: number) => value.toLocaleString() },
      { title: '申请笔数', dataIndex: 'applies', render: (value: number) => value.toLocaleString() },
      { title: '放款笔数', dataIndex: 'disburses', render: (value: number) => value.toLocaleString() },
      { title: '放款转化率', dataIndex: 'conversion', render: (value: number) => formatPercent(value) }
    ],
    []
  );

  const reborrowColumns: TableColumnsType<ReborrowRateRow> = useMemo(
    () => [
      { title: '分层', dataIndex: 'segment' },
      { title: '复借率', dataIndex: 'rate', render: (value: number) => formatPercent(value) },
      {
        title: '变化 (pp)',
        dataIndex: 'change',
        render: (value: number) => renderChangeTag(value)
      },
      { title: '样本量', dataIndex: 'volume', render: (value: number) => value.toLocaleString() }
    ],
    []
  );

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      {error && (
        <Alert
          type="error"
          message="报表中心数据拉取失败"
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
            businessDate: defaultDate,
            channel: 'all',
            product: 'all'
          }}
        >
          <div className="form-grid">
            <Form.Item label="业务日期" name="businessDate">
              <DatePicker allowClear={false} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="渠道" name="channel">
              <Select options={channelOptions} />
            </Form.Item>
            <Form.Item label="产品" name="product">
              <Select options={productOptions} />
            </Form.Item>
          </div>
          <Space>
            <Button type="primary" onClick={handleSearch}>
              查询
            </Button>
            <Button onClick={handleReset}>重置</Button>
          </Space>
        </Form>
      </Card>

      <Card title="关键指标">
        <Row gutter={[16, 16]}>
          {summaryCards.map((item) => (
            <Col key={item.label} xs={24} sm={12} md={6}>
              <Card bordered={false} style={{ background: '#f7f9fb' }}>
                <Statistic title={item.label} value={item.value} valueStyle={{ fontSize: 24 }} />
                <Space size={8} style={{ marginTop: 12 }}>
                  {renderChangeTag(item.delta)}
                  <Typography.Text type="secondary">{item.description}</Typography.Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
        <Typography.Paragraph type="secondary" style={{ marginTop: 16 }}>
          数据来源 report-svc `/reports/center`，默认每 5 分钟刷新。若连接 bff-admin，将自动替换 mock。
        </Typography.Paragraph>
        <Typography.Text type="secondary">上次更新时间：{data?.lastUpdated ?? '--'}</Typography.Text>
      </Card>

      <Card title="逾期迁移率">
        <Table<OverdueMigrationRow>
          rowKey={(record) => record.stage}
          columns={overdueColumns}
          dataSource={overdueData}
          pagination={false}
          loading={isPending || isFetching}
        />
      </Card>

      <Card title="渠道漏斗">
        <Table<ChannelFunnelRow>
          rowKey={(record) => record.channel}
          columns={channelColumns}
          dataSource={funnelData}
          pagination={false}
          loading={isPending || isFetching}
        />
      </Card>

      <Card title="复借率">
        <Table<ReborrowRateRow>
          rowKey={(record) => record.segment}
          columns={reborrowColumns}
          dataSource={reborrowData}
          pagination={false}
          loading={isPending || isFetching}
        />
      </Card>

      {notes.length > 0 && (
        <Card title="分析备注" type="inner">
          <ul style={{ paddingLeft: 16, marginBottom: 0 }}>
            {notes.map((note) => (
              <li key={note}>
                <Typography.Text>{note}</Typography.Text>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </Space>
  );
};

export default ReportCenter;
