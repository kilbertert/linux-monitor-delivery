# 仓库元数据 / Repo Meta

## 项目信息

- **项目名称**: linux-monitor
- **仓库地址**: (待创建)
- **分支策略**: master (主分支)

## 交付版本

- **版本**: 1.0.0
- **交付时间**: 2026-03-09
- **状态**: 初始功能版本

## 本地 Git 状态

- **当前分支**: master
- **最新提交**: b6985c2 - feat: 初始版本 - Linux 监控系统

## 创建远程仓库

由于当前环境无法直接创建 GitHub 仓库，请手动执行以下步骤：

### 方式 1: 使用 GitHub CLI (推荐)

```bash
# 安装 gh (如未安装)
brew install gh  # Mac
# 或
winget install GitHub.cli  # Windows

# 登录
gh auth login

# 创建私有仓库
gh repo create linux-monitor-delivery --private --source=. --push
```

### 方式 2: 使用 GitHub Web

1. 访问 https://github.com/new
2. 仓库名称: `linux-monitor-delivery`
3. 设为私有 (Private)
4. 不初始化 (No README)
5. 执行:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/linux-monitor-delivery.git
   git branch -M main
   git push -u origin main
   ```

## 交付清单

- [x] 后端代码 (FastAPI + psutil)
- [x] 前端代码 (Vue3 + ECharts)
- [x] 依赖文件
- [x] README 文档
- [x] 需求文档
- [x] 规划文档
- [x] Git 提交

---

**更新记录**:
- 2026-03-09: 初始版本代码已提交，等待创建远程仓库
