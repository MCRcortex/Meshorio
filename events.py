import socket,os,math,threading,select,struct,time
from Network import sendVar,receiveVar


class eventFactory:
    def __init__(self,network=None):
        self.socketReceive=[]
        self.toTickFuncs=[]
        self.timeoutFuncs=[]
        self.eventFunctions={}
        self.network=network
    
    def _responderThread(self):
        while True:
            time.sleep(0.010)
            if len(self.network.peers)==0:
                continue
            readable,_,errored=select.select([peer.responderSocket for peer in self.network.peers],[],[peer.responderSocket for peer in self.network.peers],0)
            for peer in readable:
                data=receiveVar(peer)
                sendVar(peer,self.eventFunctions[data[0]](peer,*data[1]))
            for peerSocket in errored:
                for peer in self.network.peers:
                    if peerSocket==peer.responderSocket:
                        self.network.removePeer(peer)
            
            
    def call(self,function,*argv,peer=None):
        if peer!=None:
            sendVar(peer.callSocket,[function,argv])
            return (peer,receiveVar(peer.callSocket))
        responses=[]
        for peer in self.network.peers:
            sendVar(peer.callSocket,[function,argv])
        for peer in self.network.peers:#faster than without secondary four loop
            responses.append((peer,receiveVar(peer.callSocket)))
        return responses
    
    def tick(self,timeout=0):#like javascript setInterval
        timeout=int(timeout/10)+1  #math.ceil
        def callback(function):
            self.toTickFuncs.append([timeout,0,function])#timeout lastTimeoutTime function
            return function
        return callback
    def responder(self,function):
        self.eventFunctions[function.__name__]=function
        return function
    
    def timeout(self,timeout,callback):#like javascript setTimeout
        timeout+=1 #cause calling a timeout of 0 would cause it too run in the same "tick"
        self.timeoutFuncs.append([timeout,callback])
    def onReceive(self,socket):
        def callback(function):
            self.socketReceive.append([socket,function])
            return function
        return callback
    def _localEventThread(self):
        while True:
            if len(self.socketReceive)!=0:
                receivable,_,_ = select.select([i[0] for i in self.socketReceive],[],[],0)
                for i in receivable:
                    for x in self.socketReceive:
                        if i==x[0]:
                            x[1](i)
            for funcStruct in self.toTickFuncs:
                funcStruct[1]=(funcStruct[1]+1)%funcStruct[0]
                if funcStruct[1]==0:
                    funcStruct[2]()
            #this is a safe way of iterating though a changing list    could maybe optimise
            temp=0
            while temp!=len(self.timeoutFuncs):
                if self.timeoutFuncs[temp][0]<=0:
                    self.timeoutFuncs[temp][1]()
                    del self.timeoutFuncs[temp]
                else:
                    self.timeoutFuncs[temp][0]-=1
                    temp+=1
            time.sleep(0.010)#10ms is the smallest delay that windows can do reliably
            
    def setup(self,network=None):
        if self.network==None:
            self.network=network
        if self.network==None:
            raise "No network handle was given"
        self.eventThread=threading.Thread(target=self._localEventThread)
        self.responderThread=threading.Thread(target=self._responderThread)
        
        self.eventThread.start()
        self.responderThread.start()
                    
                

