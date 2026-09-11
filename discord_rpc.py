
from pypresence import Presence

import time



from config import DISCORD_CLIENT_ID





rpc = Presence(DISCORD_CLIENT_ID)

rpc.connect()



rpc.update(

    details="Playing Roblox",

    state="Testing roblox-peek",

    start=time.time(),

)



print("Discord Rich Presence connected!")



while True:

    time.sleep(15)

