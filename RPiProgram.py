import socket
import cv2
import mediapipe as mp
import time

host = "localhost"  # Change this to your desired host
port = 8080  # Change this to your desired port

class MouseServer:
    def __init__(self):
        self.screenSizes = (0,0)
        self.socketObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketObj.bind((host, port))
        self.socketObj.listen(1)
        self.client_socket, self.client_address = self.socketObj.accept()

    # For receving screen sizes from client
    def receive_Data(self):
        try:
            data = self.client_socket.recv(1024).decode()
            print(f"Received data: {data}")
            self.screenSizes = tuple(map(int, data.split(",")))

        except ConnectionResetError:
            pass

    # Send mouse posistion to client
    def send_Data(self, data):
        self.client_socket.sendall(data.encode())
    
    # To limit result between 0 an 1
    def clamp(self, intInput):
        if intInput < 0:
            return 0
        elif intInput > 1:
            return 1
        else:
            return intInput
    
    def runCamera(self):
        # Initialize variables
        self.receive_Data()
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

                    # print("XIP: ", xIPos, " YIP: ", yIPos)
                    # print("XT: ", xTpos, " YT: ", yTpos)
                    
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

                        # print("XIPercent: ", xIPect, " YIPercent: ", yIPect)
                        
                        # Transfer small coordinate to big screen
                        xSIPos = xIPect * scrX
                        ySIPos = yIPect * scrY
                        xSTpos = xTPect * scrX
                        ySTpos = yTPect * scrY

                        #send XSIpos, YSIpos, XSTpos, YSTpos to client
                        self.send_Data(f"{xSIPos},{ySIPos},{xSTpos},{ySTpos}")
                        self.client_socket.recv(1)
                        

                """
                image = cv2.flip(image, 1)
                cv2.imshow("image", image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break
                """

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mouseServer = MouseServer()
    mouseServer.runCamera()