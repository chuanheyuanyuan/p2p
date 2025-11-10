import { Card, Col, Row, Typography } from 'antd';
import { opsCardsMock } from '../mocks/data';

const OpsConfig = () => (
  <Row gutter={[16, 16]}>
    {opsCardsMock.map((card) => (
      <Col xs={24} md={12} key={card.title}>
        <Card title={card.title} actions={[<span key="action">{card.action}</span>]}> 
          <Typography.Paragraph type="secondary">{card.description}</Typography.Paragraph>
        </Card>
      </Col>
    ))}
  </Row>
);

export default OpsConfig;
