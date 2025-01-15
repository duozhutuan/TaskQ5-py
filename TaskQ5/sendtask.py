 
import json
import copy
from datetime import datetime

# Import your config and key management (replace with actual Python equivalents)
from .config import channel_info, relays, relayServer 
from nostrclient.key import PrivateKey
from nostrclient.localStorage import local_storage
from nostrclient.relay_pool import RelayPool
import time
import traceback

# Constants
KIND = 42
TAGS = [['d', ''], ['e', channel_info['id'], relayServer[0], 'root']]



Keypriv = local_storage.get("Keypriv")
pkey = PrivateKey(Keypriv)
if Keypriv is None :
    local_storage.set("Keypriv",str(pkey))
print("Your public key: ",pkey.public_key)
print("Your public key bech32: ",pkey.public_key.bech32())


r = RelayPool(relays,pkey)

r.connect(0)

# wait for anyone server connect success
connected = False
while connected == False:
    for r1 in r.RelayList:
        if r1.connected == True:
            connected = True
    time.sleep(0.1)



def send_task(content):
    # Add identifier
    identifier = str(int(datetime.now().timestamp()))
    tags1 = copy.deepcopy(TAGS) # Deep copy
    tags1.append(["published_at", identifier])

    msg = {
        "kind":KIND,
        "tags":tags1,
        "content":content,
    }

    e = r.publish(msg)
    
    return e 

def update_task(task_event,pubkey):
    try:
        # Update new status
        content = json.loads(task_event.content)
        n_event = {}
        tags1 = copy.deepcopy(task_event.tags)  # Deep copy
        content['status'] = 'done'
        content['taskFinisher_pubkey'] = pubkey
        n_event["content"] = json.dumps(content)
        n_event["kind"] = KIND
        n_event["tags"] = tags1
        r.publish(n_event)

        # Delete old task
        h_event = {}
        h_event["kind"] = 5
        h_event["tags"] = [['e', task_event.id], ['k', '42']]
        h_event["content"] = "task done"
        r.publish(h_event)
    except Exception as e:
            traceback.print_exc()

def subscribe(task_event,bridge,finish_task):
    r1 = RelayPool([bridge],pkey)

    r1.connect(1)
    filters = {"kinds":[10010],"#e":[task_event.id]}
    subs = r1.subscribe(filters)
    def h1(e):
        update_task(task_event,e['pubkey'])
        finish_task(e)
        subs.close()
    subs.on("EVENT",h1)
 
