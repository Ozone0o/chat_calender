# 日程信息提取系统

这是一个基于 Flask 和 Ollama 的日程信息提取系统，能够从自然语言文本中自动提取日程相关的关键信息，包括事件名称、时间、地点和流程。

## 功能特点

- 自动从文本中提取日程信息
- 支持相对时间（如"明天"、"下周五"）的智能转换
- 实时获取系统时间，确保时间计算的准确性
- 简洁直观的用户界面
- 结构化的 JSON 数据输出

## 技术栈

- 后端：Python Flask
- 前端：HTML, CSS, JavaScript
- AI 模型：Ollama (deepseek-r1:1.5b)
- 跨域支持：Flask-CORS

## 安装说明

1. 确保已安装 Python 3.x
2. 安装必要的 Python 包：
   ```bash
   pip install flask flask-cors ollama
   ```
3. 确保 Ollama 服务已启动并运行在本地（默认端口 11434）

## 项目结构

```
chat_calender/
├── chat.py              # 后端 Flask 应用
├── templates/
│   └── index.html       # 前端界面
└── README.md            # 项目文档
```

## 使用方法

1. 启动后端服务：
   ```bash
   python chat.py
   ```
   服务将在 http://localhost:8080 运行

2. 在浏览器中访问 http://localhost:8080

3. 在文本框中输入日程信息，例如：
   ```
   明天下午3点在会议室A举行项目启动会，会议将讨论新产品的开发计划和人员分工。
   ```

4. 点击"提取信息"按钮，系统将自动提取并显示：
   - 日程名称
   - 具体时间
   - 地点
   - 流程说明

## 注意事项

- 确保 Ollama 服务正在运行
- 系统会自动使用当前时间处理相对时间表述
- 如果某些信息无法提取，将显示"无"

## 示例输出

输入：
```
明天下午3点在会议室A举行项目启动会，会议将讨论新产品的开发计划和人员分工。
```

输出：
```json
{
    "event_name": "项目启动会",
    "time": "2024-03-08 15:00",
    "location": "会议室A",
    "process": "讨论新产品的开发计划和人员分工"
}
```

## 开发说明

- 后端使用 Flask 框架处理 HTTP 请求
- 前端使用原生 JavaScript 实现异步请求
- 使用 Ollama 的 deepseek-r1:1.5b 模型进行信息提取
- 支持跨域请求，方便前后端分离部署

## 许可证

MIT License