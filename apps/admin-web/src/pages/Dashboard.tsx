import { Alert, Button, Card, Col, Progress, Row, Skeleton, Space, Statistic, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { fetchDashboardOverview } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { data, isPending, isFetching, error, refetch } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: fetchDashboardOverview,
    staleTime: 60 * 1000
  });

  const loading = isPending && !data;

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      {error && (
        <Alert
          type="error"
          message="仪表盘数据拉取失败"
          description={(error as Error).message}
          action={
            <Button size="small" onClick={() => refetch()} loading={isFetching}>
              重试
            </Button>
          }
        />
      )}
      <Card>
        <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }} wrap>
          <div>
            <Typography.Title level={5} style={{ margin: 0 }}>
              报表中心
            </Typography.Title>
            <Typography.Text type="secondary">查看渠道漏斗、复借率与逾期迁移率等指标</Typography.Text>
          </div>
          <Button type="primary" onClick={() => navigate('/report-center')}>
            前往报表中心
          </Button>
        </Space>
      </Card>
      <Row gutter={16} wrap>
        {(loading ? Array.from({ length: 4 }) : data?.kpis ?? []).map((kpi, index) => (
          <Col xs={24} sm={12} lg={6} key={kpi?.label ?? index}>
            <Card hoverable loading={loading}>
              {kpi && (
                <>
                  <Statistic title={kpi.label} value={kpi.value} valueStyle={{ fontSize: 28 }} />
                  <Typography.Text type="secondary">{kpi.delta}</Typography.Text>
                </>
              )}
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16} wrap>
        <Col xs={24} md={16}>
          <Card title="当前逾期" loading={loading}>
            {data ? (
              <>
                <Statistic value={data.overdue.rate} suffix="%" precision={2} valueStyle={{ fontSize: 32 }} />
                <Typography.Text type="secondary">
                  到期 {data.overdue.dueToday} 单 · 已还 {data.overdue.repaid} 单 · 昨日 {data.overdue.yesterdayRate}%
                </Typography.Text>
                <Progress percent={data.overdue.progress} showInfo={false} style={{ marginTop: 16 }} />
              </>
            ) : (
              <Skeleton active paragraph={false} />
            )}
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="今日催回单量" loading={loading}>
            {data ? (
              <>
                <Statistic value={data.recovery.cases} suffix="单" />
                <Typography.Text type="secondary">{data.recovery.note}</Typography.Text>
              </>
            ) : (
              <Skeleton active paragraph={false} />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} wrap>
        <Col xs={24} md={12}>
          <Card title="今日统计" loading={loading}>
            {data ? (
              <ul className="stat-list">
                <li>
                  <span>装机量</span>
                  <strong>{data.today.installs}</strong>
                </li>
                <li>
                  <span>注册人数</span>
                  <strong>{data.today.regs}</strong>
                </li>
                <li>
                  <span>登录人数</span>
                  <strong>{data.today.logins}</strong>
                </li>
                <li>
                  <span>申请笔数</span>
                  <strong>{data.today.applies}</strong>
                </li>
                <li>
                  <span>放款笔数</span>
                  <strong>{data.today.disburses}</strong>
                </li>
                <li>
                  <span>还款笔数</span>
                  <strong>{data.today.repayments}</strong>
                </li>
              </ul>
            ) : (
              <Skeleton active paragraph={{ rows: 3 }} />
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="新客申请转化率" loading={loading}>
            {data ? (
              <div className="radial-wrapper">
                <Progress type="dashboard" percent={data.conversion.percent} size={160} />
              </div>
            ) : (
              <Skeleton active paragraph={false} />
            )}
            {data && (
              <Typography.Paragraph style={{ marginTop: 12, textAlign: 'center' }}>
                {data.conversion.numerator}/{data.conversion.denominator}（申请/注册）
              </Typography.Paragraph>
            )}
          </Card>
        </Col>
      </Row>
    </Space>
  );
};

export default Dashboard;
