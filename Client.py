from socket import socket, SOL_SOCKET, SO_ERROR, gethostname, gethostbyname
import pyautogui
import time
import datetime

pyautogui.FAILSAFE = False
local_server = "10.0.0.52"
local_server_port = 8080

def getDistance(x1,y1,x2,y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

class MouseClient:
    def __init__(self):
        self.scrX, self.scrY = pyautogui.size()
        self.socketObj = socket()
        #self.socketObj.bind((local_server, 8998))
        self.socketObj.connect((local_server, local_server_port))
        
    def send_Data(self, data):
        self.socketObj.sendall(data.encode())
        
    def receive_Data(self):
        data = self.socketObj.recv(1024).decode()
        return data
    
    def close(self):
        self.socketObj.close()
    
    def runMoveMouse(self):
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
                #print(distanceIT)
                pyautogui.moveTo((XIPos + XTPos)/2, (YIPos + YTPos)/2)
                recordedTIme = datetime.datetime.now().timestamp()
                if datetime.datetime.now().timestamp() - recordedTIme < 0.5:
                    pass
                elif distanceIT < 75:
                    pyautogui.Click()
                    print("Click")
                    time.sleep(0.5)
                    recordedTIme = datetime.datetime.now().timestamp()

            connectStatus = self.socketObj.getsockopt(SOL_SOCKET, SO_ERROR)
        #self.send_Data("1")

    def exitProgram(self):
        self.send_Data("1")
        self.close()
        exit()
    
    def runClick(self):
        recordedTIme = datetime.datetime.now().timestamp()
        self.send_Data(f"{self.scrX},{self.scrY}")
        while True:
            recvData = self.receive_Data()
            #print(recvData)
            xIPos, yIPos, xTpos, yTpos, xMPos, yMPos, xPPos, yPPos = map(int, map(float, recvData.split(",")))
            print("xIPos: ", xIPos, " yIPos: ", yIPos, " xTpos: ", xTpos, " yTpos: ", yTpos, " xMPos: ", xMPos, " yMPos: ", yMPos, " xPPos: ", xPPos, " yPPos: ", yPPos)
            TIDistance = getDistance(xIPos, yIPos, xTpos, yTpos)
            MIDistance = getDistance(xTpos, yTpos, xMPos, yMPos)
            RIDistance = getDistance(xTpos, yTpos, xPPos, yPPos)

            """print("TIDistance: ", TIDistance)
            print("MIDistance: ", MIDistance)
            print("RIDistance: ", RIDistance)"""

            if datetime.datetime.now().timestamp() - recordedTIme<0.5:
                pass
            elif TIDistance < 75:
                pyautogui.click()
                print("Click")
                recordedTIme = datetime.datetime.now().timestamp()
            elif MIDistance < 75:
                pyautogui.doubleClick()
                print("Double Click")  
                recordedTIme = datetime.datetime.now().timestamp()
            
            if RIDistance < 50:
                #self.send_Data("1")
                print(1)
                self.exitProgram()
            self.send_Data("0")
            
            


if __name__ == "__main__":
    mouseClient = MouseClient()

    modeSelect = 99
    while modeSelect != 3:
        modeSelect = int(input("1. Move Mouse\n2. Click\n3. Exit\n"))
        
        if modeSelect == 1:
            mouseClient.send_Data(str(1))
            mouseClient.runMoveMouse()
            
        elif modeSelect == 2:
            mouseClient.send_Data(str(2))
            mouseClient.runClick()
            
        elif modeSelect == 3:
            mouseClient.send_Data(str(3))
            mouseClient.exitProgram()
        else:
            print("Invalid Input")
            continue