
import json
from .config   import  channel_info
from .recvtask import recv_task
from .do_requests import requestTask
from nostrclient.log import log 
import traceback

dispatch = [
    requestTask
]

def  handleEvent(Event):

   try :
        
        content = json.loads(Event["content"])
        log.red(content['url'])
        log.blue(content.get('status'))    
        for  t in dispatch:
            if  t["type"] == content["type"]:
                t["cb"](Event)    
   except Exception as e:
        traceback.print_exc()
  

recv_task(channel_info["id"],handleEvent)