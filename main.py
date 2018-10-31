from Network import *
from events import *
from rcon import SourceRcon as Rcon

import random
import os.path

event=eventFactory()#make a new event factory to handle all opperations


#IT MAY GET CAUGHT IN A DEADLOCK STATE TO FIX, in the event system, thread _tickNetworkResponder



##USE DICTIONARY AS A DB then just strinify and save too file for saving and to load, just read date and parse
if not os.path.exists("items.json"):
    items={}
else:
    items=eval(open("items.json").read())

@event.tick(600)#save every minute   -FIND OUT HOW TO MAKE PYTHON SLEEP RELIABLY    - NOT WORKING
def saveItems():
    print("HELLO")
    f=open("items.json","w")
    f.write(str(items))
    f.close()

#########################################
#Mesh callable/responder functions

@event.responder
def listAmountOfItems(peer,Items):#Return key mapping
    out={}
    for item in Items:
        if item in items.keys():
            out[item]=items[item]
    return out

@event.responder
def requestItem(peer,Item,ammount):#Returns the amount of items removed
    if Item in items.keys():
        count=min(items[Item],ammount)
        items[Item]-=count
        return count
    return 0


#With rcon factorio has a rcon.print() function which returns whats printed to the python thing, this can be used for export of items I.E. calling /exportedItems and /exportedItems then return the items to be exported 
@event.tick(75)
def exportItems():
    exportedItems=eval(rcon.rcon("/exportItems").rstrip(b'\n').decode())# [['iron',10],['copper',15]]  
    for item in exportedItems:
        print(item)
        if not item[0] in items.keys():
            items[item[0]]=0
        items[item[0]]+=item[1]

        
@event.tick(150)
def itemRequests():
    requestedItems=eval(rcon.rcon("/itemRequets").rstrip(b'\n').decode())
    responces=event.call("listAmountOfItems",[i[0] for i in requestedItems])
    requestedItems=dict(requestedItems)
    itemGotCount=requestedItems.copy()
    random.shuffle(responce)
    #CAN BE HIGHLY OPTIMISED
    for peer,responce in responces:
        for item in responce:
            if requestedItems[item]<=0:
                continue
            requestedItems[item]-=event.call("requestItem",requestItem,min(requestedItems[item],responce[item]),peer=responce[0])
    for item in requestedItems:
        itemGotCount[item]-=requestedItems[item]
    rcon.rcon("/importItems ["+",".join([str([item,itemGotCount[item]])for item in itemGotCount])+"]")
#.\factorio.exe --rcon-port 1234 --rcon-password helrgjfiduhgiufh --start-server-load-latest --no-log-rotation
rcon=Rcon('localhost',1234,'helrgjfiduhgiufh')

mesh=network("hello")#Mesh token is hello

event.setup(mesh)








































