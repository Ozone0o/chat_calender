import json
import logging
import re
from datetime import datetime

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from ollama import Client

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# ollama客户端
ollama_url = "http://localhost:11434"  # localhost可以换成你部署ollama主机的ip、远程ip
ollama_client = Client(host=ollama_url)
# 模型名称
model_name = "deepseek-r1:1.5b"


def remove_think_tags(text):
    """移除<think>标签及其内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)


def clean_json_response(text):
    """清理JSON响应中的Markdown格式"""
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)  # 移除多余的空行
    text = text.strip()  # 去除首尾空白
    return text


def parse_schedule_info(text):
    """解析日程信息，返回结构化的数据"""
    try:
        logger.info(f"开始处理文本: {text}")

        # 构建提示词
        prompt = f"""请从以下文本中提取日程信息，并以JSON格式返回：
{text}

请提取以下信息：
1. 事件名称 [理解分析内容后，如果全文只有一个明确的事件名称直接提取，如果有多个任务请概括为一个事件名称]
2. 时间 [直接提取时间，必须将时间格式指定为 YYYY-MM-DD HH:MM 或者指定为 YYYY-MM-DD]
3. 地点 [直接提取地点]
4. 流程 [理解分析内容后概括一下]

如果某项信息无法提取，请使用null表示。

请直接返回JSON格式，不要有任何其他内容。格式如下：
{{
    "event_name": "事件名称",
    "time": "时间",
    "location": "地点",
    "process": "流程"
}}"""

        logger.debug(f"发送到Ollama的提示词: {prompt}")

        # 调用Ollama客户端
        response = ollama_client.generate(
            model_name,
            prompt=prompt,
            stream=False
        )

        # 获取响应文本
        response_text = response.response
        logger.debug(f"Ollama原始响应: {response_text}")

        # 移除<think>标签
        cleaned_response = remove_think_tags(response_text)
        logger.debug(f"清理后的响应: {cleaned_response}")

        # 清理JSON响应
        json_text = clean_json_response(cleaned_response)
        logger.debug(f"清理后的JSON文本: {json_text}")

        # 尝试解析JSON
        try:
            schedule_info = json.loads(json_text)
            logger.info(f"成功解析日程信息: {schedule_info}")
            return schedule_info
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            return {
                "error": "无法解析日程信息",
                "raw_response": cleaned_response
            }

    except Exception as e:
        logger.error(f"处理日程信息时出错: {str(e)}", exc_info=True)
        return {
            "error": str(e)
        }

@app.route('/')
def index():
    # 获取当前年份和月份
    now = datetime.now()
    year = now.year
    month = now.strftime('%B')  # 例如：'April'
    return render_template('index.html', year=year, month=month)

@app.route('/send_message', methods=['POST'])
def extract_info():
    try:
        # 获取请求数据
        data = request.get_json()
        logger.info(f"收到请求数据: {data}")

        text = data.get('text')
        if not text:
            logger.warning("未提供文本")
            return jsonify({
                "error": "No text provided"
            })

        # 解析日程信息
        schedule_info = parse_schedule_info(text)
        logger.info(f"返回日程信息: {schedule_info}")

        return jsonify(schedule_info)

    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
