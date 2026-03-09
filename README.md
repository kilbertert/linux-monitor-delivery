# Linux 运行监控系统

基于 FastAPI + Vue3 的 Linux 运行监控系统毕业设计项目。

## 功能特性

- ✅ 实时 CPU 使用率监控（支持按核心统计）
- ✅ 内存使用情况监控
- ✅ 磁盘 I/O 统计
- ✅ 网络带宽监控
- ✅ SQLite 数据存储
- ✅ REST API 接口
- ✅ WebSocket 实时推送
- ✅ ECharts 可视化仪表盘

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- psutil
- SQLite3
- WebSocket

### 前端
- Vue 3 (Composition API)
- ECharts / vue-echarts
- Axios
- Vue Router

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境（可选）
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

## API 文档

服务启动后访问: http://localhost:8000/docs

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /metrics/current | 获取当前所有指标 |
| GET | /metrics/cpu | 获取 CPU 指标 |
| GET | /metrics/memory | 获取内存指标 |
| GET | /metrics/disk | 获取磁盘 I/O 指标 |
| GET | /metrics/network | 获取网络 I/O 指标 |
| GET | /metrics/history | 获取历史指标 |
| GET | /metrics/system/info | 获取系统信息 |
| WS | /ws/metrics | WebSocket 实时推送 |

### WebSocket 使用

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    metrics: ['cpu', 'memory', 'disk', 'network'],
    interval: 1
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## 项目结构

```
linux-monitor/
├── backend/
│   ├── main.py           # FastAPI 主应用
│   ├── requirements.txt  # Python 依赖
│   ├── monitor/          # 监控采集模块
│   ├── db/               # 数据库模块
│   └── api/              # API 路由
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── views/        # 页面视图
│   │   └── api/          # API 请求
│   └── package.json
└── README.md
```

## 部署

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 许可证

MIT License
