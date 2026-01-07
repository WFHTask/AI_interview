# VoiVerse AI 面试系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Gemini-3.0-4285F4.svg" alt="Gemini">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

<p align="center">
  <strong>基于 Google Gemini 3.0 的智能面试初筛平台</strong><br>
  自动化 AI 面试 | STAR 追问法 | 实时评估 | 飞书通知 | S 级人才自动录用
</p>

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [功能详解](#功能详解)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [部署指南](#部署指南)

---

## 项目简介

VoiVerse AI 面试系统是一个为远程招聘场景设计的智能面试初筛平台。系统使用 Google Gemini 3.0 大语言模型，通过 AI 面试官自动完成候选人初面，并根据岗位要求进行多维度评估打分。

### 适用场景

- **远程岗位快速补员**：无需协调面试官时间，候选人随时可参与面试
- **高并发筛选**：支持多个候选人同时面试，大幅提升筛选效率
- **标准化评估**：统一评估标准，避免主观偏见
- **S 级人才识别**：自动识别并锁定卓越人才，第一时间发出邀请

### 核心流程

```
HR 配置岗位 JD → 生成面试链接 → 候选人访问链接
       ↓
  AI 面试官进行多轮对话（STAR 追问法）
       ↓
  面试结束 → AI 判官进行评估打分
       ↓
  ┌─────────────────────────────────────┐
  │  S 级 (≥90分): 展示入职邀请卡片      │
  │  A/B 级: 显示标准结束语              │
  │  C 级 (<60分): 感谢参与              │
  └─────────────────────────────────────┘
       ↓
  飞书群推送通知（带详情链接） + 面试记录存档
```

---

## 核心特性

### 1. 双 AI 引擎架构

| 引擎 | 模型 | 职责 | 特点 |
|------|------|------|------|
| **面试官** | Gemini 3.0 Flash | 主持对话、STAR 追问 | 流式响应、低延迟 |
| **判官** | Gemini 3.0 Pro | 评估打分、决策定级 | 深度推理、结构化输出 |

### 2. STAR 追问法

AI 面试官采用 STAR (Situation, Task, Action, Result) 方法论：
- 不接受简单的"是/否"回答
- 深入挖掘候选人的实战经验
- 考察技术深度、沟通能力、远程适应性

### 3. 四级人才定级

| 等级 | 分数 | 说明 | 系统行为 |
|------|------|------|----------|
| **S 级** | ≥90 | 卓越人才 | 展示入职邀请卡片，飞书红色紧急通知 |
| **A 级** | 80-89 | 优秀 | 推荐录用，飞书绿色通知 |
| **B 级** | 60-79 | 合格 | 备选，飞书橙色通知 |
| **C 级** | <60 | 不通过 | 淘汰，飞书灰色通知 |

### 4. 三维评分体系

- **技能匹配度 (60%)**：技术栈覆盖度、实战经验真实性
- **沟通与逻辑 (20%)**：表达清晰度、逻辑自洽性
- **远程适应性 (20%)**：自驱力、异步沟通能力

### 5. 安全防护

- **Prompt 注入防护**：拒绝回答敏感信息套取
- **输入验证**：XSS/SQL 注入防护
- **速率限制**：三层限流（会话/IP/全局）
- **信息隔离**：严禁透露薪资、融资等机密

### 6. 简历解析

支持多格式简历上传：PDF 文件、图片（PNG/JPG/WEBP）、纯文本粘贴。使用 Gemini 多模态能力提取结构化信息。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                        │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  HR 管理后台  │  候选人面试   │  面试详情页   │   登录认证        │
└──────┬───────┴──────┬───────┴──────┬───────┴─────────┬─────────┘
       │              │              │                 │
┌──────┴──────────────┴──────────────┴─────────────────┴─────────┐
│                         Core Services                           │
├─────────────────────┬─────────────────────┬────────────────────┤
│   InterviewerEngine │   EvaluatorEngine   │   ResumeService    │
└─────────┬───────────┴─────────┬───────────┴────────┬───────────┘
          │                     │                    │
┌─────────┴─────────────────────┴────────────────────┴───────────┐
│                       Gemini Service                            │
│         REST API (无 SDK) | 流式响应 | JSON Schema 输出          │
└────────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
                      Google Gemini 3.0 API
```

---

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端** | Streamlit 1.28+ | 单文件部署，快速开发 |
| **后端** | Python 3.10+ | 类型注解，Pydantic 数据验证 |
| **LLM** | Google Gemini 3.0 REST API | 直接 HTTP 调用，无 SDK |
| **存储** | JSON 文件 | MVP 简单方案，按日期组织 |
| **通知** | 飞书 Webhook | 卡片消息，支持紧急标记 |

---

## 快速开始

### 环境要求

- Python 3.10+
- Google Gemini API Key

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/WFHTask/AI_interview.git
cd AI_interview

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 Gemini API Key

# 启动服务
streamlit run app.py
```

### 访问应用

- **HR 管理后台**: http://localhost:8501
- **候选人面试**: http://localhost:8501/?job=<config_id>
- **面试详情**: http://localhost:8501/?session=<session_id>

---

## 配置说明

### 环境变量 (.env)

```bash
# 必填
GEMINI_API_KEY=your_gemini_api_key_here

# 可选
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
INTERVIEWER_MODEL=gemini-3.0-flash
EVALUATOR_MODEL=gemini-3.0-pro
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
HR_USERNAME=admin
HR_PASSWORD=your_secure_password
APP_BASE_URL=http://localhost:8501
MAX_INTERVIEW_TURNS=50
```

---

## 功能详解

### HR 管理后台

- 配置岗位信息（名称、JD、开场白）
- S 级人才邀请文案和预约链接
- 生成面试链接
- 飞书通知配置
- 查看历史记录

### 候选人面试界面

- 信息填写（姓名、邮箱、简历上传）
- AI 面试官多轮对话
- 流式响应，实时显示
- 面试结束自动评估
- S 级展示入职邀请卡片

---

## API 文档

### Gemini Service

```python
from services.gemini_service import GeminiService

service = GeminiService()

# 流式生成
for chunk, signature in service.stream_generate(
    model_type="interviewer",
    contents=[{"role": "user", "parts": [{"text": "你好"}]}],
    system_instruction="你是面试官..."
):
    print(chunk, end="")
```

### Interviewer Engine

```python
from core.interviewer import create_interviewer

engine, session = create_interviewer(
    job_description="岗位 JD...",
    candidate_name="张三"
)

for chunk in engine.start_interview():
    print(chunk, end="")
```

---

## 项目结构

```
AI_interview/
├── app.py                 # 主入口
├── requirements.txt       # 依赖
├── .env.example          # 环境变量模板
├── config/               # 配置管理
├── core/                 # 核心业务 (interviewer, evaluator, prompts)
├── services/             # 外部服务 (gemini, feishu, storage)
├── components/           # Streamlit UI 组件
├── models/               # Pydantic 数据模型
├── utils/                # 工具函数 (validators, rate_limiter)
└── data/                 # 数据目录 (gitignore)
```

---

## 部署指南

### Docker

```bash
docker build -t ai-interview .
docker run -p 8501:8501 --env-file .env ai-interview
```

### Streamlit Cloud

1. 推送到 GitHub
2. 在 share.streamlit.io 创建应用
3. 配置 Secrets

---

## License

MIT License
