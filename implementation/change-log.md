# 变更日志 / Change Log

## v1.0.0 (2026-03-09)

### 新增功能

- **监控采集**
  - CPU 使用率采集（支持按核心统计）
  - 内存使用情况监控
  - 磁盘 I/O 统计
  - 网络带宽监控
  - 系统硬件信息获取

- **后端 API**
  - FastAPI REST API
  - WebSocket 实时推送
  - SQLite 数据存储
  - 健康检查接口

- **前端界面**
  - Vue3 响应式仪表盘
  - ECharts 可视化图表
  - CPU 折线图
  - 内存使用仪表盘
  - 磁盘 I/O 折线图
  - 网络带宽面积图
  - 系统信息展示

### 技术栈

- Python 3.10+ / FastAPI / psutil / SQLite3 / WebSocket
- Vue 3 / ECharts / vue-echarts / Axios / Vue Router

---

**注意**: 首次使用需安装依赖并启动后端服务，详见 README.md
