import { Button, Card, Space, Timeline } from 'antd';
import { releasesMock } from '../mocks/data';

const AppUpgrade = () => (
  <Space direction="vertical" size={24} style={{ width: '100%' }}>
    <Card title="发布记录">
      <Timeline mode="left">
        {releasesMock.map((release) => (
          <Timeline.Item key={release.version} label={release.date} color="blue">
            <strong>{release.version}</strong>
            <div>{release.highlight}</div>
          </Timeline.Item>
        ))}
      </Timeline>
      <Space style={{ marginTop: 16 }}>
        <Button type="primary">创建灰度发布</Button>
        <Button>上传安装包</Button>
      </Space>
    </Card>
  </Space>
);

export default AppUpgrade;
