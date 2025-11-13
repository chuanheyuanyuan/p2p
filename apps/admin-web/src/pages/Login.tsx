import { Card, Form, Input, Button, Typography, App as AntdApp } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import type { LoginPayload, LoginResponse } from '../types/auth';
import { adminLogin } from '../services/api';
import { selectAccessToken, useAuthStore } from '../store/auth';

const Login = () => {
  const [form] = Form.useForm<LoginPayload>();
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const accessToken = useAuthStore(selectAccessToken);
  const setSession = useAuthStore((state) => state.setSession);

  const mutation = useMutation<LoginResponse, Error, LoginPayload>({
    mutationFn: (payload) => adminLogin(payload),
    onSuccess: (session) => {
      setSession(session);
      message.success('登录成功');
      const redirectPath =
        ((location.state as { from?: { pathname?: string } } | null)?.from?.pathname as string | undefined) ??
        '/';
      navigate(redirectPath, { replace: true });
    },
    onError: (error) => {
      message.error(error.message || '登录失败，请稍后再试');
    }
  });

  if (accessToken) {
    return <Navigate to="/" replace />;
  }

  const handleFinish = (values: LoginPayload) => {
    mutation.mutate(values);
  };

  return (
    <div className="auth-container">
      <Card className="auth-card" title="InsCash Admin" bordered={false}>
        <Typography.Paragraph type="secondary" style={{ marginBottom: 24 }}>
          使用员工账号登录后台，登录将记录在审计日志中。
        </Typography.Paragraph>
        <Form form={form} layout="vertical" onFinish={handleFinish} requiredMark={false}>
          <Form.Item label="账号" name="username" rules={[{ required: true, message: '请输入账号' }]}>
            <Input placeholder="ops.lead@inscash.com" size="large" autoComplete="username" />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password placeholder="••••••••" size="large" autoComplete="current-password" />
          </Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            block
            size="large"
            loading={mutation.isPending}
            style={{ marginTop: 8 }}
          >
            登录
          </Button>
        </Form>
        <Typography.Paragraph type="secondary" style={{ marginTop: 16, fontSize: 12 }}>
          默认体验账号：ops.lead / admin123；403 表示角色无该菜单权限。
        </Typography.Paragraph>
      </Card>
    </div>
  );
};

export default Login;
