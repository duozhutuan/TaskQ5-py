from nostrclient.relay_pool import RelayPool
from nostrclient.log import log
import datetime
from nostrclient.key import PrivateKey
from nostrclient.localStorage import local_storage
from nostrclient.actions import like_event

Keypriv = local_storage.get("Keypriv")
pkey = PrivateKey(Keypriv)
if Keypriv is None :
        local_storage.set("Keypriv",str(pkey))
print("Your public key: ",pkey.public_key)
print("Your public key bech32: ",pkey.public_key.bech32())
