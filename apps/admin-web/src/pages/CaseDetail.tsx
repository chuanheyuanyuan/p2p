import { Card, Descriptions, Tabs, Timeline } from 'antd';
import { caseDetailMock } from '../mocks/data';

const CaseDetail = () => {
  const { customer, profile, history } = caseDetailMock;

  return (
    <Tabs
      defaultActiveKey="customer"
      items={[
        {
          key: 'customer',
          label: '客户信息',
          children: (
            <Card className="case-card" title="基本信息">
              <Descriptions column={3} bordered size="small">
                <Descriptions.Item label="贷款编号">{customer.loanNo}</Descriptions.Item>
                <Descriptions.Item label="申批状态">{customer.status}</Descriptions.Item>
                <Descriptions.Item label="产品名称">{customer.product}</Descriptions.Item>
                <Descriptions.Item label="用户等级">{customer.level}</Descriptions.Item>
                <Descriptions.Item label="手机号码">{customer.phone}</Descriptions.Item>
                <Descriptions.Item label="SIM 号">{customer.sim}</Descriptions.Item>
                <Descriptions.Item label="渠道">{customer.channel}</Descriptions.Item>
                <Descriptions.Item label="授权隐私">{customer.authorize}</Descriptions.Item>
                <Descriptions.Item label="设备信息">{customer.device}</Descriptions.Item>
              </Descriptions>
              <Descriptions column={3} bordered size="small" style={{ marginTop: 16 }}>
                <Descriptions.Item label="姓名">{profile.name}</Descriptions.Item>
                <Descriptions.Item label="性别">{profile.gender}</Descriptions.Item>
                <Descriptions.Item label="年龄">{profile.age}</Descriptions.Item>
                <Descriptions.Item label="教育程度">{profile.education}</Descriptions.Item>
                <Descriptions.Item label="证件类型">{profile.idType}</Descriptions.Item>
                <Descriptions.Item label="证件号码">{profile.idNo}</Descriptions.Item>
                <Descriptions.Item label="婚姻状况">{profile.married}</Descriptions.Item>
                <Descriptions.Item label="GPS">{profile.gps}</Descriptions.Item>
                <Descriptions.Item label="地址">{profile.address}</Descriptions.Item>
              </Descriptions>
              <Timeline style={{ marginTop: 24 }}>
                {history.map((item) => (
                  <Timeline.Item key={item.ts} color="blue">
                    <strong>{item.ts}</strong>
                    <div>{item.text}</div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )
        },
        { key: 'approval', label: '审批信息', children: <Card>审批节点将在接入真实数据后补充。</Card> },
        { key: 'history', label: '历史记录', children: <Card>历史记录汇总。</Card> },
        { key: 'evidence', label: '凭证', children: <Card>上传/查看凭证。</Card> }
      ]}
    />
  );
};

export default CaseDetail;
