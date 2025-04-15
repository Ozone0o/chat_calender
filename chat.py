import json
import logging
import re
from flask import Flask, request, Response, render_template, jsonify
from flask_cors import CORS
from ollama import Client
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# ollama客户端
ollama_url = "http://localhost:11434"   # localhost可以换成你部署ollama主机的ip、远程ip
ollama_client = Client(host=ollama_url)
# 模型名称
model_name = "deepseek-r1:1.5b"

def get_current_time_info():
    """获取当前系统时间信息"""
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday = weekdays[now.weekday()]
    return f"当前系统时间是：{now.strftime('%Y年%m月%d日 %H:%M:%S')} {weekday}"

def remove_think_tags(text):
    """移除<think>标签及其内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def clean_json_response(text):
    """清理JSON响应中的Markdown格式"""
    # 移除```json和```标记
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    # 移除多余的空行
    text = re.sub(r'\n\s*\n', '\n', text)
    # 移除首尾空白
    text = text.strip()
    return text

def parse_schedule_info(text):
    """解析日程信息，返回结构化的数据"""
    try:
        logger.info(f"开始处理文本: {text}")
        
        # 获取当前时间信息
        current_time_info = get_current_time_info()
        
        # 构建提示词
        prompt = f"""现在的系统时间是{current_time_info}

请从以下文本中提取日程信息，并以JSON格式返回：
{text}

提取要求：
1. 事件名称：提炼核心主题，使用"动词+核心内容"结构（如"组织党员学习"），排除时间地点和罗列项
2. 时间：必须转为YYYY-MM-DD格式，含时间戳时截取日期部分，若原文无具体日期则基于系统时间合理推算（明天→+1天，下周一→最近的下个周一）
3. 地点：保持原文完整表述，不增删字词
4. 流程：合并同类活动项，用"开展/进行...及..."句式概括，不超过50字且不与事件名称重复

若信息不存在，对应值设为null。直接返回严格合法的JSON，格式：

{{
    "event_name": "事件名称",
    "time": "时间",
    "location": "地点",
    "process": "流程"
}}

注意：
- 时间字段必须严格遵循YYYY-MM-DD格式，输出时去除具体时间（如23:21:30）
- 事件名称不得包含时间/地点词汇
- 地点需保持原文表述
- JSON使用英文双引号，无注释/额外说明
处理示例：
输入文本："（6月7日下午）党员学习、组织生活会、民主评议"
→ 事件名称："党员组织生活"
→ 流程："开展党员学习、组织生活会及民主评议"
"""

        logger.debug(f"发送到Ollama的提示词: {prompt}")

        # 调用ollama客户端
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
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
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