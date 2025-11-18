import { useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  List,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
  message
} from 'antd';
import type {
  OpsProductConfig,
  GradeConfig,
  ChannelLinkConfig,
  MessageTemplateConfig,
  ApprovalRuleConfig,
  ReleaseNote
} from '../mocks/data';
import {
  fetchOpsProducts,
  fetchGradeConfigs,
  fetchChannelLinks,
  fetchMessageTemplates,
  fetchApprovalRules,
  fetchAppReleases
} from '../services/api';

const OpsConfig = () => {
  const queryClient = useQueryClient();
  const productsQuery = useQuery({ queryKey: ['ops-products'], queryFn: fetchOpsProducts });
  const gradesQuery = useQuery({ queryKey: ['ops-grades'], queryFn: fetchGradeConfigs });
  const channelQuery = useQuery({ queryKey: ['ops-channels'], queryFn: fetchChannelLinks });
  const messageQuery = useQuery({ queryKey: ['ops-messages'], queryFn: fetchMessageTemplates });
  const approvalQuery = useQuery({ queryKey: ['ops-approval'], queryFn: fetchApprovalRules });
  const releasesQuery = useQuery({ queryKey: ['ops-releases'], queryFn: fetchAppReleases });

  const addProductMutation = useMutation({
    mutationFn: async (payload: Omit<OpsProductConfig, 'productId' | 'status'> & { status?: '启用' | '停用' }) => payload,
    onSuccess: (payload) => {
      const newProduct: OpsProductConfig = {
        productId: `P-${Date.now().toString().slice(-4)}`,
        status: payload.status ?? '启用',
        allowExtension: payload.allowExtension ?? true,
        ...payload
      } as OpsProductConfig;
      queryClient.setQueryData<OpsProductConfig[]>(['ops-products'], (prev) => [...(prev ?? []), newProduct]);
      message.success('已创建产品（模拟）');
    }
  });

  const toggleTemplateMutation = useMutation({
    mutationFn: async (template: MessageTemplateConfig) => template,
    onSuccess: (template) => {
      queryClient.setQueryData<MessageTemplateConfig[]>(['ops-messages'], (prev) =>
        (prev ?? []).map((item) => (item.id === template.id ? { ...item, active: !item.active } : item))
      );
    }
  });

  const productColumns = [
    { title: '产品 ID', dataIndex: 'productId' },
    { title: '名称', dataIndex: 'name' },
    {
      title: '额度范围',
      render: (_: any, record: OpsProductConfig) => `${record.minAmount} ~ ${record.maxAmount}`
    },
    { title: '期限', dataIndex: 'termOptions' },
    { title: 'APR', dataIndex: 'apr', render: (value: number) => `${value}%` },
    {
      title: '展期',
      dataIndex: 'allowExtension',
      render: (value: boolean) => <Tag color={value ? 'green' : 'red'}>{value ? '支持' : '不支持'}</Tag>
    },
    { title: '状态', dataIndex: 'status', render: (value: OpsProductConfig['status']) => <Tag color={value === '启用' ? 'green' : 'default'}>{value}</Tag> }
  ];

  const gradeColumns = [
    { title: '等级', dataIndex: 'grade' },
    { title: '额度上限', dataIndex: 'maxCredit', render: (value: number) => `₵${value}` },
    { title: '利率优惠', dataIndex: 'interestDiscount', render: (value: number) => `${value}%` },
    { title: '自动升级', dataIndex: 'autoUpgradeDays', render: (value: number) => `${value} 天` },
    {
      title: '升级规则',
      dataIndex: 'rules',
      render: (rules: string[]) => (
        <Space direction="vertical">
          {rules.map((rule) => (
            <Tag key={rule}>{rule}</Tag>
          ))}
        </Space>
      )
    }
  ];

  const channelColumns = [
    { title: 'ID', dataIndex: 'id' },
    { title: '名称', dataIndex: 'name' },
    { title: '渠道', dataIndex: 'channel' },
    { title: '状态', dataIndex: 'status', render: (value: ChannelLinkConfig['status']) => <Tag color={value === '上线' ? 'green' : 'orange'}>{value}</Tag> },
    { title: '转化率', dataIndex: 'conversion', render: (value: number) => `${value}%` },
    { title: '日预算', dataIndex: 'budget', render: (value: number) => `₵${value}` },
    { title: '更新时间', dataIndex: 'updatedAt' }
  ];

  const approvalColumns = [
    { title: '规则', dataIndex: 'name' },
    { title: '阶段', dataIndex: 'stage' },
    { title: '条件', dataIndex: 'condition' },
    { title: '动作', dataIndex: 'action' },
    { title: '负责人', dataIndex: 'owner' },
    { title: '更新时间', dataIndex: 'updatedAt' }
  ];

  const releaseColumns = [
    { title: '版本', dataIndex: 'version' },
    { title: '日期', dataIndex: 'date' },
    { title: '亮点', dataIndex: 'highlight' }
  ];

  const productFormInitial = useMemo(
    () => ({
      name: '新产品',
      minAmount: 100,
      maxAmount: 1000,
      termOptions: '7D',
      apr: 20,
      allowExtension: true
    }),
    []
  );

  return (
    <Tabs
      items={[
        {
          key: 'products',
          label: '产品配置',
          children: (
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
              <Card title="新增产品">
                <Form
                  layout="inline"
                  initialValues={productFormInitial}
                  onFinish={(values) => addProductMutation.mutate(values)}
                >
                  <Form.Item name="name" label="名称" rules={[{ required: true }]}>
                    <Input style={{ width: 160 }} />
                  </Form.Item>
                  <Form.Item name="minAmount" label="最小额度" rules={[{ required: true }]}>
                    <InputNumber min={0} style={{ width: 120 }} />
                  </Form.Item>
                  <Form.Item name="maxAmount" label="最大额度" rules={[{ required: true }]}>
                    <InputNumber min={0} style={{ width: 120 }} />
                  </Form.Item>
                  <Form.Item name="termOptions" label="期限" rules={[{ required: true }]}>
                    <Input style={{ width: 120 }} placeholder="例：7D/14D" />
                  </Form.Item>
                  <Form.Item name="apr" label="APR" rules={[{ required: true }]}>
                    <InputNumber min={0} style={{ width: 120 }} addonAfter="%" />
                  </Form.Item>
                  <Form.Item name="allowExtension" label="支持展期" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={addProductMutation.isPending}>
                      新增
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
              <Card>
                <Table rowKey="productId" columns={productColumns} dataSource={productsQuery.data ?? []} loading={productsQuery.isPending} pagination={false} />
              </Card>
            </Space>
          )
        },
        {
          key: 'grades',
          label: '等级管理',
          children: <Table rowKey="grade" columns={gradeColumns} dataSource={gradesQuery.data ?? []} loading={gradesQuery.isPending} pagination={false} />
        },
        {
          key: 'channels',
          label: '渠道链接',
          children: <Table rowKey="id" columns={channelColumns} dataSource={channelQuery.data ?? []} loading={channelQuery.isPending} pagination={false} />
        },
        {
          key: 'messages',
          label: '消息模板',
          children: (
            <List
              loading={messageQuery.isPending}
              dataSource={messageQuery.data ?? []}
              renderItem={(template: MessageTemplateConfig) => (
                <List.Item
                  actions={[
                    <Switch
                      key="toggle"
                      checked={template.active}
                      onChange={() => toggleTemplateMutation.mutate(template)}
                    />,
                    <Button key="preview" type="link" onClick={() => message.info(template.preview)}>
                      预览
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={`${template.name} · ${template.channel}`}
                    description={`变量：${template.variables.join(', ')}`}
                  />
                </List.Item>
              )}
            />
          )
        },
        {
          key: 'approval',
          label: '审批策略',
          children: <Table rowKey="id" columns={approvalColumns} dataSource={approvalQuery.data ?? []} loading={approvalQuery.isPending} pagination={false} />
        },
        {
          key: 'releases',
          label: 'App 版本',
          children: <Table rowKey="version" columns={releaseColumns} dataSource={releasesQuery.data ?? []} loading={releasesQuery.isPending} pagination={false} />
        }
      ]}
    />
  );
};

export default OpsConfig;
