# 需求标准化文档 / Normalized Requirement

## 项目概述

- **项目名称**: 基于 FastAPI + Vue3 的 Linux 运行监控系统的设计和实现
- **项目标识**: linux-monitor
- **需求来源**: 毕设开题报告
- **交付语言**: zh-CN

## 一、项目目标

构建一套轻量级的 Linux 监控系统，能够：
1. 实时采集 CPU、内存、磁盘 I/O、网络带宽等系统指标
2. 通过网页动态展示监控数据
3. 支持历史数据查询
4. 实现实时数据推送

## 二、必做功能 (Must-Have)

### 2.1 监控数据采集模块
- [ ] CPU 使用率采集（支持按核心统计）
- [ ] 内存使用情况（总内存、可用内存、使用率）
- [ ] 磁盘 I/O 统计（读写次数、字节数、速率）
- [ ] 网络带宽统计（发送/接收字节数、带宽利用率）
- [ ] 采集周期可配置（默认 1 秒）

### 2.2 数据存储模块
- [ ] SQLite3 作为后端存储
- [ ] 按时间戳存储监控数据
- [ ] 建立索引支持历史查询

### 2.3 后端服务模块
- [ ] FastAPI REST API
  - `/metrics/current` - 返回最新指标
  - `/metrics/history` - 历史区间查询（参数：start_time, end_time）
  - `/system/info` - 返回系统硬件信息
- [ ] WebSocket 实时推送服务
- [ ] 后台定时采集任务

### 2.4 前端展示模块
- [ ] Vue3 单页应用
- [ ] ECharts 可视化：
  - CPU 使用率折线图
  - 内存使用仪表盘
  - 磁盘 I/O 折线图
  - 网络带宽面积图
- [ ] 数据实时刷新（WebSocket 或轮询）
- [ ] 响应式界面

### 2.5 部署环境
- [ ] 虚拟机中部署测试
- [ ] uvicorn 运行 FastAPI
- [ ] Vite 构建 Vue3 前端

## 三、选做功能 (Nice-to-Have)

- [ ] 多客户端并发支持
- [ ] 告警机制
- [ ] 支持更多监控指标（进程、容器等）
- [ ] 数据导出功能

## 四、技术约束

- **Python 版本**: Python 3.x（建议 3.10+）
- **后端框架**: FastAPI
- **前端框架**: Vue3 (Composition API)
- **数据库**: SQLite3
- **可视化**: Apache ECharts
- **运行环境**: Linux (Ubuntu/CentOS 虚拟机)

## 五、验收标准

### 功能验收
1. CPU、内存、磁盘、网络指标采集准确（与 top、vmstat 对比）
2. REST API 返回正确 JSON 数据
3. WebSocket 连接稳定，推送频率正常
4. 前端图表正确渲染，数据实时更新

### 性能验收
1. 采集程序 CPU 占用 < 5%
2. 采集程序内存占用 < 50MB
3. API 响应时间 < 100ms
4. 图表刷新延迟 < 1 秒

### 可用性验收
1. 浏览器访问界面流畅
2. 多客户端可同时访问
3. 异常输入有合理处理

## 六、风险与不确定项

1. **psutil 精度**: 首次调用 cpu_percent() 返回 0，需丢弃首次结果
2. **SQLite 并发**: 高并发写入可能需要优化
3. **WebSocket 稳定性**: 长连接需要心跳机制
4. **浏览器兼容性**: ECharts 兼容性测试

## 七、数据库设计

### 表结构

```sql
-- CPU 统计
CREATE TABLE cpu_stat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    cpu_percent REAL NOT NULL,
    cpu_per_core TEXT,  -- JSON: [{"core": 0, "percent": 10.5}, ...]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 内存统计
CREATE TABLE memory_stat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    total REAL NOT NULL,
    available REAL NOT NULL,
    percent REAL NOT NULL,
    used REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 网络统计
CREATE TABLE net_stat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    bytes_sent INTEGER NOT NULL,
    bytes_recv INTEGER NOT NULL,
    pack_sent INTEGER NOT NULL,
    pack_recv INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 磁盘 I/O 统计
CREATE TABLE disk_stat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    read_count INTEGER NOT NULL,
    write_count INTEGER NOT NULL,
    read_bytes INTEGER NOT NULL,
    write_bytes INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_cpu_timestamp ON cpu_stat(timestamp);
CREATE INDEX idx_memory_timestamp ON memory_stat(timestamp);
CREATE INDEX idx_net_timestamp ON net_stat(timestamp);
CREATE INDEX idx_disk_timestamp ON disk_stat(timestamp);
```

## 八、API 接口规范

### REST API

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | /metrics/current | 获取当前最新指标 | - |
| GET | /metrics/history | 获取历史指标 | start_time, end_time, metric_type |
| GET | /system/info | 获取系统信息 | - |
| GET | /metrics/cpu | 获取 CPU 指标 | - |
| GET | /metrics/memory | 获取内存指标 | - |
| GET | /metrics/disk | 获取磁盘指标 | - |
| GET | /metrics/network | 获取网络指标 | - |

### WebSocket

| 事件 | 方向 | 说明 |
|------|------|------|
| subscribe | Client -> Server | 订阅指标（JSON: {metrics: ["cpu", "memory"], interval: 1}）|
| data | Server -> Client | 推送数据（JSON: {cpu: {...}, memory: {...}, ...}）|
| unsubscribe | Client -> Server | 取消订阅 |

---

**文档版本**: 1.0  
**创建时间**: 2026-03-09  
**状态**: 需求冻结
