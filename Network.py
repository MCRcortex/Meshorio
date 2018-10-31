import socket,os,math,threading,select,struct  ,time  
DEFAULT_PORT=34199


def receiveVar(socket,raw=False):
    length=struct.unpack("!Q",socket.recv(8))[0]
    data=b''
    while length!=len(data):
        data+=socket.recv(length-len(data))
    if raw:
        return data
    return eval(data.decode())#add system to check for malishis strings

def sendVar(socket,variable,package_string=True,packet_size=4028):
    if isinstance(variable,str) and package_string:
        variable="'"+variable+"'"
    variable=str(variable).encode()#WONT WORK WITH STRING
    encodedLength=struct.pack("!Q",len(variable))
    socket.send(encodedLength)
    while len(variable)!=0:
        packet=variable[:packet_size]
        variable=variable[len(packet):]
        socket.send(packet)

class peerConnection:
    def __init__(self):
        self.callSocket=None
        self.remote_address=None
        self.responderSocket=None
        

class network:
    def __init__(self,meshToken,remote_address=None,local_address=('localhost',DEFAULT_PORT)):
        self.peers=[]
        self.local_address=local_address
        self.token=meshToken

        if remote_address!=None:
            self.peers.append(self._connectToPeer(remote_address,True))
            peer_addresses=receiveVar(self.peers[-1].callSocket)
            for peer_address in peer_addresses:
                self.peers.append(self._connectToPeer(peer_address))
            print("Succesfully connected to mesh network"+"\n",end="")
        self._runListener()
    
    def _connectToPeer(self,address,request_peer_listings=False):
        peer=peerConnection()
        peer.remote_address=address
        
        peer.callSocket=socket.socket()
        peer.callSocket.connect(address)
        sendVar(peer.callSocket,self.token,False)
        if not receiveVar(peer.callSocket):
            print("ERROR: peer did not accept our token"+"\n",end="")
            exit()
               
        peer.responderSocket=socket.socket()
        peer.responderSocket.connect(address)
        sendVar(peer.responderSocket,self.token,False)
        if not receiveVar(peer.responderSocket):
            print("ERROR: peer did not accept our token"+"\n",end="")
            exit()

        sendVar(peer.callSocket,self.local_address)
        sendVar(peer.callSocket,request_peer_listings)

        return peer
        
    def _runListener(self):
        def listen(self):
            self.server=socket.socket()
            self.server.bind(self.local_address)
            self.server.listen(9999999)#yes that is just a randomly large number
            while True:
                conn,addr=self.server.accept()
                if receiveVar(conn,True)!=self.token.encode():
                    sendVar(conn,False)
                    conn.close()
                    continue
                sendVar(conn,True)

                peer=peerConnection()
                peer.responderSocket=conn

                conn,addr=self.server.accept()
                if receiveVar(conn,True)!=self.token.encode():
                    sendVar(conn,False)
                    conn.close()
                    continue
                sendVar(conn,True)
                
                peer.callSocket=conn
                peer.remote_address=receiveVar(peer.responderSocket)
                if receiveVar(peer.responderSocket):
                    sendVar(peer.responderSocket,[peer.remote_address for peer in self.peers])

                self.peers.append(peer)
                
                print("Peer connected with address of "+addr[0]+"\n",end="")
        self.listen_thread=threading.Thread(target=listen,args=(self,))
        self.listen_thread.start()
    def removePeer(self,peer):
        del self.peers[self.peers.index(peer)]
    
if __name__=="__main__":
    mesh1=network("HELLOOOOOOOO")
    for i in range(50):
        mesh2=network("HELLOOOOOOOO",('localhost',DEFAULT_PORT),('localhost',34197-i))








#CONNECTION PROCEDUE to a new node
#peer connects to mesh node - this will be the call socket
#peer sends mesh authentication token
#if mesh node rejects token, send false and close the connection, else send true
#peer connects to mesh node again (MAYBE HAVE THE MESH NODE CONNECT TO THE PEER) - this will be the responder socket
#peer sends mesh authentication token
#if mesh node rejects token, send false and close the connection, else send true
#peer sends listenting local address via the call Socket
#peer sends false (if it is not the first connection to the mesh) to not recive all other peers on the network via the call Socket
















