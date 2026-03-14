# AI 南瓜智能伴侣

基于 DeepSeek API 的智能对话伴侣，支持多会话、自定义名字与性格。

## 功能

- **主题**：AI 南瓜智能伴侣
- **侧边栏**：新建会话、历史会话列表、底部配置
- **配置**：名字 / 性格（对应 API 的 system 配置）
- **主页面**：左右对话气泡、底部输入框

## 安装

```bash
pip3 install -r requirements.txt
```

## 启动

```bash
python3 app.py
```

浏览器访问：http://localhost:5001

## 环境变量（可选）

- `DEEPSEEK_API_KEY`：DeepSeek API 密钥，不设置则使用默认值

## 数据

会话与配置保存在 `data/sessions.json`。
