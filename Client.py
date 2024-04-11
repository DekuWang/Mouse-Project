from socket import socket, SOL_SOCKET, SO_ERROR
import pyautogui
import time

pyautogui.FAILSAFE = False
local_server = "localhost"
local_server_port = 8080

def getDistance(x1,y1,x2,y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

class MouseClient:
    def __init__(self):
        self.scrX, self.scrY = pyautogui.size()
        self.socketObj = socket()
        self.socketObj.connect((local_server, local_server_port))
        
    def send_Data(self, data):
        self.socketObj.sendall(data.encode())
        
    def receive_Data(self):
        data = self.socketObj.recv(1024).decode()
        return data
    
    def close(self):
        self.socketObj.close()
    
    def run(self):
        self.send_Data(f"{self.scrX},{self.scrY}")
        connectStatus = self.socketObj.getsockopt(SOL_SOCKET, SO_ERROR)
        print(connectStatus)
        while connectStatus == 0:
            data = self.receive_Data()
            xyList = data.split(",")
            #print(xyList)
            XIPos, YIPos, XTPos, YTPos = map(int, map(float, xyList))
            self.send_Data("0")

            distanceIT = getDistance(XIPos, YIPos, XTPos, YTPos)

            if  distanceIT >= 100:
                #print("Yes")
                pyautogui.moveTo(XIPos, YIPos)

            
            elif distanceIT < 100:
                print(distanceIT)
                pyautogui.moveTo((XIPos + XTPos)/2, (YIPos + YTPos)/2)

                if distanceIT < 50:
                    #pyautogui.doubleClick()
                    print("Double Click")
                    time.sleep(0.5)

            connectStatus = self.socketObj.getsockopt(SOL_SOCKET, SO_ERROR)
        self.send_Data("1")
            


if __name__ == "__main__":
    mouseClient = MouseClient()
    mouseClient.run()