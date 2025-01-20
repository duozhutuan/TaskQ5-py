
import time
from .config import relays 
from nostrclient.relay_pool import RelayPool
from nostrclient.log import log 
import json
import threading
import traceback
r = RelayPool(relays)
r.connect(0)


def time_since(created_at):
    now = time.time()
    time_difference = now - created_at

    seconds = int(time_difference)
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    print(f"New event publish at {days}天 {hours % 24}小时 {minutes % 60}分钟 {seconds % 60}秒 之前")
    return days

lock = threading.Lock()
bridge_pool = {}

def check_expire_bridge():
    now = time.time()
    for b in bridge_pool.keys():
        # 5 hours
        if now - bridge_pool[b]['time'] > 3600 * 5:
            del bridge_pool[b]

def publish(event,resp,pkey):
    global bridge_pool
    content = json.loads(event['content'])
    bridge = content['Bridge']

    if isinstance(bridge, str):
        bridge = [bridge]


    with lock:
      if len(bridge_pool) >= 10:
          bridge_pool = {}

      binfo = bridge_pool.get(str(bridge))
      if binfo:
          r1 = binfo['r']
          #update time
          bridge_pool[str(bridge)] = {"r":r1,"time":time.time()}

      else:
          r1 = RelayPool(bridge,pkey)
          r1.connect(5)
          bridge_pool[str(bridge)] = {"r":r1,"time":time.time()}
   
    r1.publish({'kind':10010,"content":resp,"tags":[ ["e",event["id"]] ]})
    
    check_expire_bridge()

def recv_task(eventid,handlerEvent):

    filters = {"kinds":[42],"#e":[eventid],"limit":30}
    subs = r.subscribe(filters)

    def h(e):
        try:
            
            content = json.loads(e['content'])
            days = time_since(e['created_at'])
            # Tasks exceeding one day will no longer be processed.
            if days:
                return 
            eventThread = threading.Thread(target=handlerEvent,args=(e,))
            eventThread.start()
        except Exception as e:
            traceback.print_exc()

         
    subs.on("EVENT",h)



