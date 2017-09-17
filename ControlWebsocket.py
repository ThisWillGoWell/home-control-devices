#https://www.tutorialspoint.com/python/python_multithreading.htm

import websocket
import threading
import json
import time

class serverSocket(threading.Thread):
    SERVER_URL = "ws://192.168.1.10:8080/ws"
    sock = None
    connected = False
    msgQueue = []


    def __init__(self,ipaddr=SERVER_URL, initMsg = []):
        threading.Thread.__init__(self)
        self.threadID = 'control-socket'
        self.initMsg = initMsg
        self.sock = websocket.WebSocketApp(ipaddr , on_message = self.on_message, on_error=self.on_error, on_close = self.on_close)
        self.sock.on_open = self.on_open



    def run(self):
        while True:
            self.sock.run_forever()
            print("socketDisconnected")
            time.sleep(10)




    """
    Functions that are used to get stuff from this socket
    """
    def is_connected(self):
        return self.connected

    def get_message(self):
        if len(self.msgQueue) != 0:
            return self.msgQueue.pop()
        return None


    """
    Functions that are used to send data to the server
    """
    def get(self, system, what, otherParams=[], callOnInit=False):
        lst = {'op': 'get', 'system' : system, 'what' : what}
        for param in otherParams:
            lst[param] = otherParams[param]
        if callOnInit:
            self.initMsg.append(json.dumps(lst))
        self.send(json.dumps(lst))

    def set(self, system, what,to, otherParams=[], callOnInit=False):
        lst = {'op': 'set', 'system' : system, 'what' : what, 'to':to}
        for param in otherParams:
            lst[param] = otherParams[param]
        if callOnInit:
            self.initMsg.append(json.dumps(lst))
        self.send(json.dumps(lst))  
    
    def subscribe(self, system, what='',otherParams=[], callOnInit=False ):
        if what == '':
            lst = {'op' : 'subscribe', 'type':'change', 'system' : system}
        else:
            lst = {'op' : 'subscribe','type':'change', 'system' : system, 'what':what}
        for param in otherParams:  
            lst[param] = otherParams[param]
        if callOnInit:
            self.initMsg.append(json.dumps(lst))
        self.send(json.dumps(lst))

    def alert(self, system, phrase, callOnInit=False):
        lst = {'op': 'subscribe','type':'alert','system':system, 'alertPhrase': phrase}
        if callOnInit:
            self.initMsg.append(json.dumps(lst))
        self.send(json.dumps(lst))

    """
    Functions that handel the websocket conenctions
    """

    def on_message(self, ws, msg):
        self.msgQueue.append(msg)

    def on_error(self, ws, error):  
        print(error)
        pass

    def on_close(self,ws):
        print("connection closed")
        self.connected = False
        pass

    
    def on_open(self, ws):
        self.connected = True
        self.msgQueue = []
        print("connected")
        for msg in self.initMsg:
            self.send(msg)
        
   
    def send(self, msg):
        self.sock.send(msg)

def main():
    s = serverSocket()
    s.start() 
    run = True
    while run:
        if s.is_connected():
            s.subscribe('HVAC', 'state')
            while run:
                k = s.get_message()
                if k != None:
                    print(k)
            while True:
                pass
        
                    



if __name__ == '__main__':
    main()



