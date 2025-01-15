import json
import asyncio
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Callable, Optional
from .nostrBridge import connect_bridge,send_message
from .sendtask import send_task, update_task,pkey,subscribe
from .recvtask import publish
from nostrclient.log import log


Keypub = str(pkey.public_key)
# 设置 requests 的超时时间
requests_timeout = 5  # 5秒

def do_request(content: Dict[str, Any], times: int = 0) -> None:
    """
    发送 HTTP 请求并处理响应
    """
    log.blue(content['url'])
    headers = json.loads(content['headers']) if isinstance(content['headers'], str) else content['headers']

    try:
        response = requests.get(
            content['url'],
            headers=headers,
            stream=True,
            timeout=requests_timeout
        )

        log.green(f"done,{len(response.text)}")

        response_data = {'status': response.status_code, 'data': response.text, 'headers': dict(response.headers)}

    except RequestException as error:
        if times < 3:
            response_data = do_request(content, times + 1)
        else:
            return None

    return response_data
    
def send_request(req_task: Dict[str, Any], finish_task: Callable) -> None:
    """
    发送请求到桥接器
    """
    task_event =  send_task(json.dumps(req_task))

    subscribe(task_event,req_task['Bridge'],finish_task)

def recv_request(data: Dict[str, Any]) -> Optional[str]:
    """
    接收请求并处理
    """
    if data.get('content') is None:
        return 

    content = json.loads(data['content'])

    log.blue(f"{content['clientId']}")

    if content.get('status') == 'done':
        return None

    resp = do_request(content)
    if resp:
        publish(data,json.dumps(resp),pkey)
    

# 导出的任务对象
requestTask = {
    "type": "requests",
    "cb": recv_request
}
