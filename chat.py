import json
import logging
import re
from flask import Flask, request, Response
from ollama import Client

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ollama客户端
ollama_url = "http://localhost:11434"   # localhost可以换成你部署ollama主机的ip、远程ip
ollama_client = Client(host=ollama_url)
# 模型名称
model_name = "deepseek-r1:1.5b"

def remove_think_tags(text):
    """移除<think>标签及其内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

# 系统提示词
system_prompt = """你是一个日程信息提取助手。请严格按照以下格式输出，不要有任何解释、思考过程或其他内容。

输入文本：
{text}

输出格式（直接填写，不要添加任何其他文字）：
日程名称：[理解分析内容后，如果有明确的日程名称直接提取，如果有多个任务请概括为一个日程名称]
时间：[直接提取时间]
地点：[直接提取地点]
流程：[理解分析内容后概括一下]

如果某项信息无法提取，请写"无"。"""

@app.route('/extract', methods=['POST', 'GET'])
def extract_info():
    try:
        # 接收文本
        text = request.args.get('text')
        logger.debug(f"Received text: {text}")
        
        if not text:
            return Response("data: " + json.dumps({'error': 'No text provided'}) + "\n\n", 
                           mimetype='text/event-stream')
        
        def generate():
            try:
                # 构建完整的提示词
                full_prompt = system_prompt.format(text=text)
                logger.debug(f"Sending prompt to Ollama: {full_prompt}")
                
                # 调用ollama客户端
                response_generator = ollama_client.generate(
                    model_name,
                    prompt=full_prompt,
                    stream=True
                )
                
                # 收集完整的响应
                full_response = ""
                for part in response_generator:
                    response_text = part.response
                    full_response += response_text
                
                # 移除<think>标签及其内容
                cleaned_response = remove_think_tags(full_response)
                
                # 发送清理后的响应
                data = f"data: {json.dumps({'response': cleaned_response})}\n\n"
                yield data
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in generate: {str(e)}", exc_info=True)
                error_data = f"data: {json.dumps({'error': str(e)})}\n\n"
                yield error_data
                yield "data: [DONE]\n\n"
                
        resp = Response(generate(), mimetype='text/event-stream')
        # 设置响应头
        resp.headers['Cache-Control'] = 'no-cache'
        resp.headers['Connection'] = 'keep-alive'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲

        return resp
    except Exception as e:
        logger.error(f"Error in extract_info: {str(e)}", exc_info=True)
        return Response("data: " + json.dumps({'error': str(e)}) + "\n\n", 
                       mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')  # 允许外部访问