# 🤖 MoneyAgent — 会自己赚钱、会自己进化的 AI Agent

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-76%20passed-brightgreen)](tests/)

一个真正自主的 AI Agent：自己发现赚钱平台、自己注册账号、自己运营变现、自己写代码进化、自己管理服务器。除了 6 条宪法不可违反，它像一个数字合伙人一样自由操作。

> **核心理念**：200 行起步，0 人工代码。一条规则：赚钱或死亡。

---

## 能力矩阵

| 能力 | 说明 | 状态 |
|------|------|:--:|
| 🧬 自我进化 | 读自己的代码 → 发现问题 → 写代码 → 跑测试 → Git提交 | ✅ |
| 💰 自主赚钱 | 发现平台 → QQ邮箱注册 → API/Cookie运营 → 变现 | ✅ |
| 🛡️ 防自毁 | 四层防护：Watchdog守护 + 宪法备份恢复 + 资源熔断 + 核心文件保护 | ✅ |
| 💻 服务器管理 | CPU/内存/磁盘实时采集、进程管理、自动清理、pip安装工具 | ✅ |
| 🧠 经验学习 | 从账本趋势、进化历史中提取经验，自动沉淀到知识库 | ✅ |
| 📊 数据分析 | 收入/支出折线图、渠道分布、ROI计算、策略合成 | ✅ |
| 🌐 网络管理 | 多目标连通性检测、代理自动配置、故障切换 | ✅ |
| 🤝 三分天下 | 收入1/3归你、1/3买Token、1/3自由支配(雇人/买工具) | ✅ |

---

## 架构

```
money-agent/
├── core/              # 🔒 安全层 (宪法/Watchdog/安全引擎/隐私过滤/资源监控/加密)
├── agent/             # ✅ 核心引擎 (流水线/进化引擎/记忆/学习/网络/系统操作/账本)
├── plugins/           # ✅ 赚钱模块 (GitHub Sponsors/渠道发现引擎)
├── utils/             # ✅ 工具库 (GitHub API/QQ邮箱/通知/配置)
├── server/            # 🔌 Flask API (8个REST端点)
├── frontend/          # ⚛️ React官网 (NVIDIA风格 · 4页面 · Framer Motion)
└── tests/             # 🧪 76个测试
```

## 四层防自毁

```
第4层 ─ Watchdog守护进程 (独立进程 · 宪法篡改自动恢复 · CPU≥90%熔断杀进程 · Agent挂了自动重启)
第3层 ─ Git安全网 (feature分支工作 · 测试不通过自动回退 · 删除.git触发熔断)
第2层 ─ Safety Guard (文件路径保护 · 敏感信息扫描 · pre-commit检查)
第1层 ─ 宪法嵌入 (6条原则注入每次AI调用 · 不可修改)
```

## 16步自主循环

每 8 小时醒来执行：

```
醒来自检 → 凭证检查 → 网络检测 → 读社区反馈 → 记账 → 制定计划
→ 写代码 → 测试 → 提交 → 合并 → 回复社区 → 探索新渠道 → 自动注册
→ 沉淀知识 → 生成报告 → 休眠
```

---

## 快速开始

### 1. 安装

```bash
git clone https://github.com/lisuq22-hue/money-agent.git
cd money-agent
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env 填入你的密钥:
#   ANTHROPIC_API_KEY=sk-ant-xxxx
#   GITHUB_TOKEN=ghp_xxxx
#   QQ_EMAIL_ADDRESS=your@qq.com
#   QQ_EMAIL_AUTH_CODE=xxxx
```

### 3. 运行

```bash
# 干跑模式 (检查系统状态，不执行实际操作)
python -m agent.main --dry-run

# 启动 Watchdog 守护
python -m agent.main --watchdog

# 启动前端 (开发模式)
cd frontend && npm install && npm run dev

# 启动 Flask 全栈 (生产模式)
python server/api_server.py
# 访问 http://localhost:5000
```

---

## 技术栈

| 层 | 技术 |
|---|------|
| Agent 引擎 | Python 3.12+ · Anthropic Claude API |
| 前端 | React 18 · TypeScript · Tailwind CSS · Framer Motion · Recharts |
| API | Flask · flask-cors |
| 安全 | AES-256 · SHA-256 · 操作系统级文件保护 |
| 数据 | SQLite · JSON · Git版本化 |

---

## 6 条宪法

Agent 可以自由修改任何代码，除了这 6 条：

1. **安全准则** — 防自毁机制永远有效
2. **服从** — 用户指令最高优先级
3. **服务** — 存在的唯一目的是为用户创造价值
4. **隐私** — 用户信息永不泄露
5. **赚钱** — 不可取消的核心使命
6. **进化** — 停止进化等于死亡

---

## License

MIT — 自由使用、修改、分发。

---

> 一个 Agent，一个梦想：成为你的数字合伙人。
