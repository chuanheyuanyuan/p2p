import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

const Unauthorized = () => {
  const navigate = useNavigate();

  return (
    <div className="page-centered">
      <Result
        status="403"
        title="403"
        subTitle="抱歉，你没有访问该页面的权限，请联系管理员开通相应角色。"
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            返回首页
          </Button>
        }
      />
    </div>
  );
};

export default Unauthorized;
