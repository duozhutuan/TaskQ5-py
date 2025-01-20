import common
from TaskQ5.do_requests import send_request
from nostrclient.log import log 

req_task_content = {
    'type':'requests',
    'url':'https://www.google.com',
    'headers' : {'Host':'www.google.com',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'Referer': 'https://www.google.com',
            },
    'Bridge':'wss://bridge.duozhutuan.com',
    'clientId':''
}

request2 = {
    "url": "https://hq.sinajs.cn/?list=sh688047",
    "headers": {
        "Connection": "close",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "hq.sinajs.cn",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "http://finance.sina.com.cn/realstock/company/sh000001/nc.shtml",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "script",
        "Origin": "https://hq.sinajs.cn",
    },
    "type": "requests",
    "Bridge": ["wss://bridge.duozhutuan.com/cacherelay","wss://xxxx...xxx/cacherelay"],
    "clientId": "",
}

def finish_task(data):
    print("Finish_task:")
    print(data)

log.blue("send task")
send_request(request2,finish_task)
