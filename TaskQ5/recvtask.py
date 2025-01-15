
import time
from .config import relays 
from nostrclient.relay_pool import RelayPool
from nostrclient.log import log 
import json
import threading
import traceback

r = RelayPool(relays)


r.connect(0)

# wait for anyone server connect success
connected = False
while connected == False:
    for r1 in r.RelayList:
        if r1.connected == True:
            connected = True
    time.sleep(0.1)


def time_since(created_at):
    now = time.time()
    time_difference = now - created_at

    seconds = int(time_difference)
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    print(f"New event publish at {days}天 {hours % 24}小时 {minutes % 60}分钟 {seconds % 60}秒 之前")


def publish(event,resp,pkey):
    content = json.loads(event['content'])    
    r1 = RelayPool([content['Bridge']],pkey)
    r1.connect(1)
    r1.publish({'kind':10010,"content":resp,"tags":[ ["e",event["id"]] ]})

def recv_task(eventid,handlerEvent):

    filters = {"kinds":[42],"#e":[eventid],"limit":30}
    subs = r.subscribe(filters)

    def h(e):
        try:
            
            content = json.loads(e['content'])
            time_since(e['created_at'])
            eventThread = threading.Thread(target=handlerEvent,args=(e,))
            eventThread.start()
        except Exception as e:
            traceback.print_exc()

         
    subs.on("EVENT",h)
