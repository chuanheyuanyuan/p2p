import { Card, Col, Progress, Row, Space, Statistic, Typography } from 'antd';
import { dashboardKpis } from '../mocks/data';

const Dashboard = () => {
  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <Row gutter={16} wrap>
        {dashboardKpis.map((kpi) => (
          <Col xs={24} sm={12} lg={6} key={kpi.label}>
            <Card hoverable>
              <Statistic title={kpi.label} value={kpi.value} valueStyle={{ fontSize: 28 }} />
              <Typography.Text type="secondary">{kpi.delta}</Typography.Text>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16} wrap>
        <Col xs={24} md={16}>
          <Card title="当前逾期">
            <Statistic value={89.16} suffix="%" precision={2} valueStyle={{ fontSize: 32 }} />
            <Typography.Text type="secondary">应还：166 · 已还：18 · 昨日逾期率 45.61%</Typography.Text>
            <Progress percent={65} showInfo={false} style={{ marginTop: 16 }} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="今日催回单量">
            <Statistic value={0} suffix="单" />
            <Typography.Text type="secondary">今日已分配 0 · 催收团队待命</Typography.Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} wrap>
        <Col xs={24} md={12}>
          <Card title="今日统计">
            <ul className="stat-list">
              <li>
                <span>注册人数</span>
                <strong>1</strong>
              </li>
              <li>
                <span>申请笔数</span>
                <strong>27</strong>
              </li>
              <li>
                <span>放款笔数</span>
                <strong>15</strong>
              </li>
            </ul>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="新客申请转化率">
            <div className="radial-wrapper">
              <Progress type="dashboard" percent={0} size={160} />
            </div>
          </Card>
        </Col>
      </Row>
    </Space>
  );
};

export default Dashboard;
