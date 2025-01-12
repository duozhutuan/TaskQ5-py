import json
import asyncio
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Callable, Optional
from .nostrBridge import connect_bridge,send_message
from .sendtask import send_task, update_task,pkey

from nostrclient.log import log


Keypub = str(pkey.public_key)
# 设置 requests 的超时时间
requests_timeout = 5  # 5秒

def do_request(content: Dict[str, Any], callback: Callable, times: int = 0) -> None:
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
        callback(response_data)

    except RequestException as error:
        
        if times < 3:
            do_request(content, callback, times + 1)
        else:
            callback(None)

# 处理发送消息的逻辑
def handle_send_message(socket, message: Dict[str, Any], req_task: Dict[str, Any],
                              finish_task: Callable, progress_value: Dict[str, Any]) -> None:
    """
    处理从桥接器接收到的消息
    """
    print("progressValue", progress_value['val'], progress_value['status'])

    if message['action'] == "clientId":
        req_task["clientId"] = message['content']
        print("clientId:", message['content'])
        task_event =  send_task(json.dumps(req_task))

    if message['action'] == 'message':
        content = message['message']
        if content['type'] == 'ping':
            if progress_value['status'] == 0 or progress_value['val'] < 3:
                send_message(socket, message['from'], message['to'], {'type': 'pong'})
                progress_value['status'] = 1
                progress_value['val'] += 1
            else:
                send_message(socket, message['from'], message['to'], {'type': 'taskTaken'})

        if content['type'] == 'response':
            progress_value['status'] = 2
            print("Done EventId: ", content['eventid'])
            update_task(req_task, content['eventid'], content['identifer'], content['pubkey'])
            finish_task(content)
            socket.close()

def send_request(req_task: Dict[str, Any], finish_task: Callable) -> None:
    """
    发送请求到桥接器
    """
    progress_value = {'val': 0, 'status': 0}
    connect_bridge(req_task['Bridge'], lambda socket, message:  
        handle_send_message(socket, message, req_task, finish_task, progress_value))

# 处理接收消息的逻辑
def handle_recv_message(socket, message: Dict[str, Any], req_content: Dict[str, Any]) -> int:
    """
    处理接收到的消息
    """
    if message['action'] == "clientId":
        client_id = message['content']
        send_message(socket, req_content['clientId'], client_id, {'type': 'ping'})
        return 302

    if message['action'] == "message":
        if message.get('code') != 200:
            return message['code']

        content = message['message']
        if content['type'] == "taskTaken":
            return 200

        if content['type'] == "pong":
            def callback(response):
                print("callback")
                if response is None:
                    return 500
                log.green(f"{req_content['id']}, {len(response['data'])}")
                
                send_message(socket, message['from'], message['to'], {
                        'type': "response",
                        'response': {
                            'status': response['status'],
                            'data': response['data'],
                            'headers': response['headers']
                        },
                        'eventid': req_content['id'],
                        'pubkey': Keypub,
                        'identifer': req_content['identifer']
                    })
                
                return 200

            do_request(req_content, callback)
            return 200

    return 404



def recv_request(data: Dict[str, Any]) -> Optional[str]:
    """
    接收请求并处理
    """
    content = json.loads(data['content'])

    log.blue(f"{content['clientId']}")

    if content.get('status') == 'done':
        return None

    content['id'] = data['id']
    content['identifer'] = data['tags'][0][1]

    
    if content.get('Bridge') and content.get('clientId'):
        def bridge_handler(socket, message):
            code = handle_recv_message(socket, message, content)
            if code == 200:
                socket.close()
                return 'recv done'
            if code in (404, 502):
                socket.close()
                return 'target offline'

        connect_bridge(content['Bridge'], bridge_handler)
    else:
        return 'requests version not match'

# 导出的任务对象
requestTask = {
    "type": "requests",
    "cb": recv_request
}