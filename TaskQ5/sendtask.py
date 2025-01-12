 
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
    tags1[0][1] = identifier
    tags1.append(["published_at", identifier])

    msg = {
        "kind":KIND,
        "tags":tags1,
        "content":content,
    }

    e = r.publish(msg)
    
    return e 

def update_task(content, event_id, identifier, pubkey):
    try:
     if content.get('status') != 'done':
        # Update new status
        n_event = {}
        tags1 = copy.deepcopy(TAGS)  # Deep copy
        tags1[0][1] = identifier
        tags1.append(["published_at", identifier])
        content['status'] = 'done'
        content['taskFinisher_pubkey'] = pubkey
        n_event["content"] = json.dumps(content)
        n_event["kind"] = KIND
        n_event["tags"] = tags1
        r.publish(n_event)

        # Delete old task
        h_event = {}
        h_event["kind"] = 5
        h_event["tags"] = [['e', event_id], ['k', '42']]
        h_event["content"] = "task done"
        r.publish(h_event)
    except Exception as e:
            traceback.print_exc()

