import json
import websocket
from nostrclient.log import log  # 假设你有一个 log.py 文件，并且里面有 log 对象
import threading



bridge_buffer = {}

def connect_bridge(url, onmessage):
    global bridge_buffer

    def on_open(ws):
        log.cyan('recv a task from relay server, connected to Bridge server execute task')

    def on_message(ws, message):

        message_data = json.loads(message)
        onmessage(ws, message_data)

    # 创建 WebSocket 连接
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
    )

    bridge_buffer[url] = ws     
    # 启动 WebSocket 连接
    ws.run_forever()

    # 启动 WebSocket 连接
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    return ws

def send_message(ws, to, from_, message):

    message_data = {
        'action': 'message',
        'code': 200,
        'from': from_,
        'to': to,
        'message': message
    }
    ws.send(json.dumps(message_data))