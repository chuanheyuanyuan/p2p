const content = document.getElementById('content');
const navButtons = document.querySelectorAll('.nav-item');

const mock = {
  kpis: [
    { label: '今日放款金额', value: '₵93,800', delta: '+12.6% vs 昨日' },
    { label: '今日申请笔数', value: '27', delta: '首逾率 38.19%' },
    { label: '登录人数', value: '15', delta: '老客 14 · 新客 1' },
    { label: '催回金额', value: '₵0', delta: '今日已分配 0 单' }
  ],
  dailyStats: [
    { date: '2025-10-20', installs: 48, regs: 1, logins: 0, applies: 27, disburses: 15, repayments: 15, amount: 93800 },
    { date: '2025-10-19', installs: 197, regs: 7, logins: 7, applies: 110, disburses: 54, repayments: 25, amount: 20195 },
    { date: '2025-10-18', installs: 233, regs: 10, logins: 7, applies: 163, disburses: 109, repayments: 79, amount: 44296 },
    { date: '2025-10-17', installs: 256, regs: 11, logins: 12, applies: 197, disburses: 117, repayments: 117, amount: 45500 }
  ],
  applications: [
    { id: '397709', product: 'InsCash Plus', name: 'Chiamaka Eddy-okafor', channel: 'Google Ads', level: 'Level5', amount: 150, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
    { id: '397708', product: 'InsCash Max', name: 'Nancy A. Osei', channel: 'Facebook Ads', level: 'Level5', amount: 550, term: '7D', reviewer: 'OCR 编辑', status: '通过' },
    { id: '397706', product: 'InsCash Pro', name: 'Samuel Adu', channel: 'Facebook Ads', level: 'Level1', amount: 5000, term: '180D', reviewer: 'OCR 编辑', status: '拒绝' }
  ],
  collections: [
    { caseId: 'CASE-1001', user: 'Nancy Osei', bucket: 'D1', amount: 520, assignee: 'Team A', due: '2025-10-21', status: '工作中' },
    { caseId: 'CASE-1002', user: 'Samuel Adu', bucket: 'D7', amount: 1450, assignee: 'Team A', due: '2025-10-14', status: 'PTP 10/22' },
    { caseId: 'CASE-1003', user: 'Kobby Gomez', bucket: 'D15', amount: 2880, assignee: 'Team B', due: '2025-10-05', status: '转外包' }
  ],
  caseDetail: {
    customer: {
      name: 'Nancy Agyapomaa Osei',
      level: 'Level5',
      product: 'InsCash Max',
      phone: '553****75',
      sim: 'HuZH6t+k3HuVOTHlHC3i5Q==',
      status: '还款期',
      device: 'itel P671L',
      channel: 'Facebook Ads',
      authorize: '已授权',
      submitAt: '2025-10-20 08:06:08'
    },
    profile: {
      gender: '女',
      age: 35,
      education: '大学',
      idType: '身份证',
      idNo: 'GHA-718571472-2',
      address: 'Ashanti Bantama BA 52',
      married: '未婚',
      gps: '6.6021, -1.6246'
    },
    history: [
      { ts: '2025-10-20 09:02', text: '案件创建，分配 Team A' },
      { ts: '2025-10-20 11:31', text: '坐席外呼：客户承诺 10/22 全额还款' },
      { ts: '2025-10-20 18:05', text: '发送催收短信' }
    ]
  }
};

const views = {
  dashboard: renderDashboard,
  dailyStats: renderDailyStats,
  applications: renderApplications,
  collections: renderCollections,
  caseDetail: renderCaseDetail,
  ops: renderOps,
  upgrade: renderUpgrade
};

navButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    navButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    render(btn.dataset.view);
  });
});

function render(view) {
  const handler = views[view] || views.dashboard;
  handler();
}

function renderDashboard() {
  content.innerHTML = `
    <h2 class="section-title">系统总览</h2>
    <div class="cards">
      ${mock.kpis
        .map(
          (kpi) => `
            <article class="card">
              <h4>${kpi.label}</h4>
              <strong>${kpi.value}</strong>
              <small>${kpi.delta}</small>
            </article>
          `
        )
        .join('')}
    </div>
    <div class="cards">
      <article class="card" style="grid-column: span 2;">
        <h4>当前逾期</h4>
        <strong>89.16</strong>
        <div style="height: 6px; background:#e2e8f0; border-radius:999px; margin: 14px 0;">
          <div style="width:65%; background:#2563eb; height:100%; border-radius:999px;"></div>
        </div>
        <small>应还: 166 · 已还: 18 · 昨日逾期率 45.61%</small>
      </article>
      <article class="card">
        <h4>今日催回单量</h4>
        <strong>0</strong>
        <small>今日已分配 0 · 催收团队待命</small>
      </article>
      <article class="card">
        <h4>设备情况</h4>
        <strong>48</strong>
        <small>安卓 92% · iOS 8%</small>
      </article>
    </div>
    <div class="cards">
      <article class="card">
        <h4>今日统计</h4>
        <p>注册人数：1</p>
        <p>申请笔数：27</p>
        <p>放款笔数：15</p>
      </article>
      <article class="card">
        <h4>新客申请转化率</h4>
        <div style="height: 160px; display:flex; align-items:center; justify-content:center;">
          <div style="width:120px; height:120px; border:8px solid #e2e8f0; border-radius:50%; position:relative;">
            <div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:24px; color:#94a3b8;">0%</div>
          </div>
        </div>
      </article>
    </div>
  `;
}

function renderDailyStats() {
  content.innerHTML = `
    <div class="section-title">平台每日统计</div>
    <div class="inline-form">
      <label>时间范围
        <input type="text" value="2025-10-11 ~ 2025-10-20" readonly />
      </label>
      <label>是否复借
        <select><option>全部</option><option>是</option><option>否</option></select>
      </label>
      <label>渠道
        <select><option>全部渠道</option><option>Facebook</option><option>Google</option></select>
      </label>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>日期</th>
            <th>安装量</th>
            <th>注册人数</th>
            <th>登录人数</th>
            <th>申请笔数</th>
            <th>放款笔数</th>
            <th>还款笔数</th>
            <th>放款金额 (GHS)</th>
          </tr>
        </thead>
        <tbody>
          ${mock.dailyStats
            .map(
              (row) => `
                <tr>
                  <td>${row.date}</td>
                  <td>${row.installs}</td>
                  <td>${row.regs}</td>
                  <td>${row.logins}</td>
                  <td>${row.applies}</td>
                  <td>${row.disburses}</td>
                  <td>${row.repayments}</td>
                  <td>${row.amount.toLocaleString()}</td>
                </tr>
              `
            )
            .join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderApplications() {
  content.innerHTML = `
    <div class="section-title">全部申请</div>
    <div class="filters">
      <label>手机号<input placeholder="输入手机号" /></label>
      <label>申请时间<input value="2025-07-19 ~ 2025-10-20" /></label>
      <label>贷款类型<select><option>全部</option><option>InsCash Max</option></select></label>
      <label>用户等级<select><option>全部</option><option>Level5</option></select></label>
      <label>申请渠道<select><option>全部</option><option>Facebook Ads</option><option>Google Ads</option></select></label>
      <label>App版本<select><option>全部</option><option>1.0.17</option></select></label>
      <label>申请状态<select><option>全部</option><option>通过</option><option>拒绝</option></select></label>
      <label>放款发放时间<input type="text" placeholder="开始 ~ 结束" /></label>
    </div>
    <div class="button-row" style="margin-bottom:16px;">
      <button class="button-primary">查询</button>
      <button class="button-ghost">重置</button>
      <button class="button-ghost">导出</button>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>贷款编号</th>
            <th>产品名称</th>
            <th>用户姓名</th>
            <th>申请渠道</th>
            <th>用户等级</th>
            <th>金额</th>
            <th>期限</th>
            <th>申请时间</th>
            <th>审核员</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          ${mock.applications
            .map(
              (row) => `
                <tr>
                  <td><a href="#">${row.id}</a></td>
                  <td>${row.product}</td>
                  <td>${row.name}</td>
                  <td>${row.channel}</td>
                  <td>${row.level}</td>
                  <td>${row.amount}</td>
                  <td>${row.term}</td>
                  <td>2025-10-20 08:06</td>
                  <td>${row.reviewer}</td>
                  <td><span class="badge">${row.status}</span></td>
                </tr>
              `
            )
            .join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderCollections() {
  content.innerHTML = `
    <div class="section-title">催收案件</div>
    <div class="filters">
      <label>案件号<input placeholder="输入案件号" /></label>
      <label>Bucket<select><option>全部</option><option>D0</option><option>D1</option><option>D7</option></select></label>
      <label>催收员<select><option>全部</option><option>Team A</option><option>Team B</option></select></label>
      <label>承诺状态<select><option>全部</option><option>PTP</option><option>坏账</option></select></label>
    </div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>案件号</th>
            <th>借款人</th>
            <th>Bucket</th>
            <th>逾期金额</th>
            <th>分案团队</th>
            <th>到期日</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          ${mock.collections
            .map(
              (row) => `
                <tr>
                  <td>${row.caseId}</td>
                  <td>${row.user}</td>
                  <td>${row.bucket}</td>
                  <td>${row.amount}</td>
                  <td>${row.assignee}</td>
                  <td>${row.due}</td>
                  <td>${row.status}</td>
                </tr>
              `
            )
            .join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderCaseDetail() {
  const { customer, profile, history } = mock.caseDetail;
  content.innerHTML = `
    <div class="section-title">案件详情 · 还款期</div>
    <div class="tabs">
      <div class="tab active">客户信息</div>
      <div class="tab">审批信息</div>
      <div class="tab">历史记录</div>
      <div class="tab">凭证</div>
    </div>
    <div class="case-card">
      <h5>基本信息</h5>
      <div class="inline-form">
        <label>贷款编号<div>${customer.loanNo || '397708'}</div></label>
        <label>申批状态<div>${customer.status}</div></label>
        <label>产品名称<div>${customer.product}</div></label>
        <label>用户等级<div>${customer.level}</div></label>
        <label>手机号码<div>${customer.phone}</div></label>
        <label>SIM号<div>${customer.sim}</div></label>
        <label>渠道<div>${customer.channel}</div></label>
        <label>授权隐私<div>${customer.authorize}</div></label>
        <label>设备信息<div>${customer.device}</div></label>
      </div>
    </div>
    <div class="case-card" style="background:#f0fdf4; border-color:#bbf7d0;">
      <h5>个人信息</h5>
      <div class="inline-form">
        <label>姓名<div>${profile.name}</div></label>
        <label>性别<div>${profile.gender}</div></label>
        <label>年龄<div>${profile.age}</div></label>
        <label>教育程度<div>${profile.education}</div></label>
        <label>证件类型<div>${profile.idType}</div></label>
        <label>证件号码<div>${profile.idNo}</div></label>
        <label>婚姻状况<div>${profile.married}</div></label>
        <label>GPS<div>${profile.gps}</div></label>
        <label>地址<div>${profile.address}</div></label>
      </div>
    </div>
    <div class="case-card" style="background:#eef2ff; border-color:#c7d2fe;">
      <h5>历史记录</h5>
      <div class="timeline">
        ${history
          .map(
            (item) => `
              <div class="timeline-item">
                <span>${item.ts}</span>
                <div>${item.text}</div>
              </div>
            `
          )
          .join('')}
      </div>
    </div>
  `;
}

function renderOps() {
  content.innerHTML = `
    <div class="section-title">运营管理 · 配置面板</div>
    <div class="cards">
      ${['账号与角色管理', '产品与用户等级管理', '支付管理', '申请审批配置', '消息模板管理', '渠道链接管理']
        .map(
          (item) => `
            <article class="card">
              <h4>${item}</h4>
              <p style="min-height:48px;">维护后台导航、权限、模板与风控策略，支持即拍即改。</p>
              <button class="button-ghost">进入配置</button>
            </article>
          `
        )
        .join('')}
    </div>
  `;
}

function renderUpgrade() {
  content.innerHTML = `
    <div class="section-title">App 包与升级管理</div>
    <div class="card">
      <h4>发布记录</h4>
      <div class="timeline">
        <div class="timeline-item">
          <span>2025-10-15 · v1.0.17</span>
          <div>新增隐私合规弹窗、修复闪退</div>
        </div>
        <div class="timeline-item">
          <span>2025-09-30 · v1.0.16</span>
          <div>优化注册链路、集成 Kochava</div>
        </div>
        <div class="timeline-item">
          <span>2025-09-10 · v1.0.15</span>
          <div>上线新催收模板</div>
        </div>
      </div>
      <div class="button-row" style="margin-top:16px;">
        <button class="button-primary">创建灰度发布</button>
        <button class="button-ghost">上传安装包</button>
      </div>
    </div>
  `;
}

// 初始渲染
document.addEventListener('DOMContentLoaded', () => {
  render('dashboard');
});
