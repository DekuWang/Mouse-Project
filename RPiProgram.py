import socket
import cv2
import mediapipe as mp
import time

host = ""  # Change this to your desired host
port = 8080  # Change this to your desired port

def getDistance(x1,y1,x2,y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

class MouseServer:
    def __init__(self):
        self.funcMode = 99
        self.runningCode = 0
        self.screenSizes = (0,0)
        self.socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketObj.bind((host, port))
        self.socketObj.listen(1)
        self.client_socket, self.client_address = self.socketObj.accept()
        print(f"Connection from {self.client_address}")

    # For receving screen sizes from client
    def receive_SCR_Size(self):
        try:
            data = self.client_socket.recv(1024).decode()
            print(f"Received data: {data}")
            self.screenSizes = tuple(map(int, data.split(",")))

        except ConnectionResetError:
            pass

    # Send mouse posistion to client
    def send_Data(self, data):
        self.client_socket.sendall(data.encode())

    def modeSetting(self):
        self.funcMode = int(self.client_socket.recv(1024).decode())
        if self.funcMode == 1:
            self.runCameraMoveMouse()
        elif self.funcMode == 2:
            self.runCameraClick()
        elif self.funcMode == 3:
            self.client_socket.close()
            self.socketObj.close()
            exit()

    # To limit result between 0 an 1
    def clamp(self, intInput):
        if intInput < 0:
            return 0
        elif intInput > 1:
            return 1
        else:
            return intInput
    
    def runCameraMoveMouse(self):
        # Initialize variables
        self.receive_SCR_Size()
        scrX, scrY = self.screenSizes
        winX, winY = scrX * 2//3, scrY * 2//3
        rectStart = (winX//2 - 2 * winX//10, winY//2 - 2 * winY//10)
        rectEnd = (winX//2 + 2 * winX//10, winY//2 + 2 * winY//10)
        
        xStart, xEnd = rectStart[0], rectEnd[0]
        yStart, yEnd = rectStart[1], rectEnd[1]

        mp_holistic = mp.solutions.holistic
        cap = cv2.VideoCapture(0) # capture using main camera

        with mp_holistic.Holistic() as holistic:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    continue
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                rectWidth = xEnd - xStart
                rectHeight = yEnd - yStart

                if results.right_hand_landmarks:

                    #Index finger Position for WINDOWS
                    xIPos = winX * (1 - results.right_hand_landmarks.landmark[8].x)
                    yIPos = winY * (results.right_hand_landmarks.landmark[8].y)
                    #Thumb Position for WINDOWS
                    xTpos = winX * (1 - results.right_hand_landmarks.landmark[4].x)
                    yTpos = winY * results.right_hand_landmarks.landmark[4].y
                    
                    #if xIPos > xStart and xIPos < xEnd and yIPos > yStart and yIPos < yEnd, and give some tolerance:
                    if xIPos > (xStart - winX//15) and xIPos < (xEnd + winX //15) and yIPos > (yStart - winY//15) and yIPos < (yEnd + winY//15):
                        
                        # calculate percentage
                        xIPect = (xIPos - xStart)/ rectWidth
                        yIPect = (yIPos - yStart)/ rectHeight

                        xTPect = (xTpos - xStart)/ rectWidth
                        yTPect = (yTpos - yStart)/ rectHeight

                        # bunch of stupid codes
                        xIPect = self.clamp(xIPect)
                        yIPect = self.clamp(yIPect)
                        xTPect = self.clamp(xTPect)
                        yTPect = self.clamp(yTPect)
                        
                        # Transfer small coordinate to big screen
                        xSIPos = xIPect * scrX
                        ySIPos = yIPect * scrY
                        xSTpos = xTPect * scrX
                        ySTpos = yTPect * scrY

                        #send XSIpos, YSIpos, XSTpos, YSTpos to client
                        self.send_Data(f"{xSIPos},{ySIPos},{xSTpos},{ySTpos}")
                        self.client_socket.recv(1)

        cap.release()
        cv2.destroyAllWindows()

    def runCameraClick(self):
        self.receive_SCR_Size()
        scrX, scrY = self.screenSizes

        mp_holistic = mp.solutions.holistic
        cap = cv2.VideoCapture(0) # capture using main camera

        with mp_holistic.Holistic() as holistic:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    continue
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.right_hand_landmarks:

                    #Index finger Position for WINDOWS
                    xIPos = scrX * (1 - results.right_hand_landmarks.landmark[8].x)
                    yIPos = scrY * (results.right_hand_landmarks.landmark[8].y)
                    #Thumb Position for WINDOWS
                    xTpos = scrX * (1 - results.right_hand_landmarks.landmark[4].x)
                    yTpos = scrY * results.right_hand_landmarks.landmark[4].y
                    #Middle finger Position for WINDOWS
                    xMPos = scrX * (1 - results.right_hand_landmarks.landmark[12].x)
                    yMPos = scrY * results.right_hand_landmarks.landmark[12].y
                    #Pinky finger Position for WINDOWS
                    xPPos = scrX * (1 - results.right_hand_landmarks.landmark[20].x)
                    yPPos = scrY * results.right_hand_landmarks.landmark[20].y

                    if getDistance(xTpos, yTpos, xMPos, yMPos) < 75 or getDistance(xTpos, yTpos, xPPos, yPPos) < 75 or getDistance(xIPos, yIPos, xTpos, yTpos) < 75:
                        self.send_Data(f"{xIPos},{yIPos},{xTpos},{yTpos},{xMPos},{yMPos},{xPPos},{yPPos}")
                        self.runningCode = int(self.client_socket.recv(1).decode())
                #print(self.runningCode)

        cap.release()
        cv2.destroyAllWindows()
                    


#if __name__ == "__main__":
try:
    mouseServer = MouseServer()
    mouseServer.modeSetting()
except Exception as e:
    print("Progress Ended")
    input("Press Enter to exit")
