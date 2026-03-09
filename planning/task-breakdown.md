# 任务拆解 / Task Breakdown

## 项目: linux-monitor

---

## 阶段 1: 项目骨架 (对应 M2)

### T1.1 项目结构创建

**输入**: 需求文档  
**输出**: 目录结构  

**步骤**:
1. 创建 backend/ 目录（后端）
2. 创建 frontend/ 目录（前端）
3. 创建 docs/ 目录（文档）

**验证**: 目录存在且结构正确

**DoD**: 目录结构符合预期

---

### T1.2 后端环境搭建

**输入**: Python 环境  
**输出**: requirements.txt, 可运行的后端

**步骤**:
1. 创建 requirements.txt
2. 安装依赖: `pip install fastapi uvicorn psutil websockets sqlalchemy`
3. 创建 main.py 入口文件
4. 运行验证: `uvicorn main:app --reload`

**验证**: 
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/docs
```

**DoD**: FastAPI 服务启动成功，/docs 可访问

---

### T1.3 前端环境搭建

**输入**: Node.js 环境  
**输出**: 可运行的 Vue3 项目

**步骤**:
1. 使用 Vite 创建 Vue3 项目: `npm create vite@latest frontend -- --template vue`
2. 安装依赖: `npm install echarts vue-echarts axios`
3. 构建验证: `npm run build`

**验证**:
```bash
cd frontend
npm install
npm run dev
```

**DoD**: Vue3 开发服务器可启动

---

## 阶段 2: 后端核心 (对应 M3.1)

### T2.1 监控数据采集模块

**输入**: psutil 库  
**输出**: 可复用的采集函数

**步骤**:
1. 创建 backend/monitor/collector.py
2. 实现 CPU 采集函数
3. 实现内存采集函数
4. 实现磁盘 I/O 采集函数
5. 实现网络带宽采集函数
6. 单元测试验证

**验证**:
```python
from monitor.collector import get_cpu, get_memory, get_disk, get_network
print(get_cpu())
```

**DoD**: 所有采集函数返回正确数据

---

### T2.2 SQLite 存储模块

**输入**: 采集数据  
**输出**: 持久化的数据库

**步骤**:
1. 创建 backend/db/init_db.py（数据库初始化）
2. 创建 backend/db/models.py（数据模型）
3. 创建 backend/db/crud.py（增删改查）
4. 初始化数据库表
5. 验证数据写入

**验证**:
```bash
python -c "from db.init_db import init_db; init_db()"
ls -la monitor.db
```

**DoD**: 数据库创建成功，表结构正确

---

### T2.3 REST API 实现

**输入**: 采集模块 + 存储模块  
**输出**: 可访问的 API 接口

**步骤**:
1. 创建 backend/api/metrics.py（指标接口）
2. 实现 /metrics/current
3. 实现 /metrics/history
4. 实现 /system/info
5. 添加定时采集任务
6. API 文档测试

**验证**:
```bash
curl http://localhost:8000/metrics/current
curl http://localhost:8000/metrics/history?start_time=xxx&end_time=xxx
curl http://localhost:8000/system/info
```

**DoD**: 所有接口返回正确 JSON

---

### T2.4 WebSocket 实时推送

**输入**: 采集数据流  
**输出**: WebSocket 连接

**步骤**:
1. 创建 backend/api/websocket.py
2. 实现 WebSocket 端点 /ws/metrics
3. 实现订阅/取消订阅协议
4. 实现定时推送
5. 前端联调测试

**验证**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

**DoD**: WebSocket 连接稳定，数据实时推送

---

## 阶段 3: 前端核心 (对应 M3.2)

### T3.1 页面布局与路由

**输入**: Vue3 初始项目  
**输出**: 可用的页面结构

**步骤**:
1. 创建 frontend/src/views/Dashboard.vue
2. 创建 frontend/src/components/
3. 配置路由 (Vue Router)
4. 基础布局 (Header, Sidebar, Content)

**验证**: 页面可渲染，路由可跳转

**DoD**: 页面结构完整

---

### T3.2 API 请求模块

**输入**: 后端 API  
**输出**: 前端请求封装

**步骤**:
1. 创建 frontend/src/api/index.js
2. 封装 axios 实例
3. 创建请求函数 (getCurrentMetrics, getHistoryMetrics, getSystemInfo)
4. 添加错误处理

**验证**:
```javascript
import { getCurrentMetrics } from '@/api';
const data = await getCurrentMetrics();
console.log(data);
```

**DoD**: API 请求正常工作

---

### T3.3 ECharts 图表组件

**输入**: ECharts 库  
**输出**: 可复用的图表组件

**步骤**:
1. 创建 frontend/src/components/CpuChart.vue
2. 创建 frontend/src/components/MemoryGauge.vue
3. 创建 frontend/src/components/DiskChart.vue
4. 创建 frontend/src/components/NetworkChart.vue
5. 配置图表选项
6. 测试渲染

**验证**: 图表正确渲染，数据正确更新

**DoD**: 4 个图表组件可用

---

### T3.4 数据实时刷新

**输入**: WebSocket 连接  
**输出**: 实时更新的仪表盘

**步骤**:
1. 在 Dashboard.vue 集成 WebSocket
2. 实现数据订阅逻辑
3. 实现图表数据更新
4. 处理连接断开/重连

**验证**: 图表数据每 N 秒自动更新

**DoD**: 实时数据展示正常

---

## 阶段 4: 测试与优化 (对应 M4)

### T4.1 功能测试

**步骤**:
1. 采集准确性对比 (top, vmstat)
2. API 异常输入测试
3. WebSocket 稳定性测试 (24h)

**DoD**: 所有测试通过

---

### T4.2 性能测试

**步骤**:
1. 资源占用测试 (CPU, Memory)
2. API 响应时间测试
3. 并发测试

**DoD**: 满足性能指标

---

## 阶段 5: 交付 (对应 M5)

### T5.1 GitHub 仓库创建

**步骤**:
1. 创建 GitHub 私有仓库
2. 初始化 git
3. 添加 .gitignore
4. 首次提交
5. 推送到远程

**验证**: 仓库可 clone

**DoD**: 代码已推送

---

### T5.2 文档完善

**步骤**:
1. 编写 README.md（部署说明）
2. 编写 API 文档
3. 编写使用说明

**DoD**: 文档完整可读

---

## 任务优先级

| 优先级 | 任务 | 预估工时 |
|--------|------|----------|
| P0 | T2.1 监控采集 | 4h |
| P0 | T2.2 SQLite 存储 | 3h |
| P0 | T2.3 REST API | 4h |
| P0 | T2.4 WebSocket | 3h |
| P0 | T3.3 图表组件 | 6h |
| P1 | T1.2 后端环境 | 2h |
| P1 | T1.3 前端环境 | 2h |
| P1 | T3.1 页面布局 | 2h |
| P1 | T3.2 API 请求 | 2h |
| P1 | T3.4 实时刷新 | 3h |
| P2 | T4.1 功能测试 | 4h |
| P2 | T4.2 性能测试 | 3h |
| P2 | T5.1 GitHub 交付 | 2h |
| P2 | T5.2 文档完善 | 3h |

---

**更新记录**:
- 2026-03-09: 任务拆解完成
