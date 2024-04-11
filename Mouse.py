import mediapipe as mp
import pyautogui
import cv2
import time

pyautogui.FAILSAFE = False

scrX, scrY = pyautogui.size()
winX, winY = scrX * 2//3, scrY * 2//3
rectStart = (winX//2 - 2 * winX//10, winY//2 - 2 * winY//10)
rectEnd = (winX//2 + 2 * winX//10, winY//2 + 2 * winY//10)

'''print(rectStart, rectEnd)
print(winX, winY)'''

xStart, xEnd = rectStart[0], rectEnd[0]
yStart, yEnd = rectStart[1], rectEnd[1]

print(scrX, scrY)

print("yStart: ", yStart, " yEnd: ", yEnd)

def getDistance(x1,y1,x2,y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5 

"""mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles"""

mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(0)

"""cap.set(3, winX)
cap.set(4, winY)"""

with mp_holistic.Holistic() as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            #print("Ignore empty camera frame")
            continue
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        """ Draw a Rectangle, commeted because wrong position 
        cv2.rectangle(image, 
                      pt1 = rectStart, 
                      pt2 =  rectEnd,
                      color = (255,0,0),
                      thickness = 1)
        """
        rectWidth = xEnd - xStart
        rectHeight = yEnd - yStart

        # draw right hand
        """        mp_drawing.draw_landmarks(
            image,
            results.right_hand_landmarks, 
            mp_holistic.HAND_CONNECTIONS   
        )"""

        if results.right_hand_landmarks:

            #Index finger Position for WINDOWS
            xIPos = winX * (1 - results.right_hand_landmarks.landmark[8].x)
            yIPos = winY * (results.right_hand_landmarks.landmark[8].y)
            #Thumb Position for WINDOWS
            xTpos = winX * (1 - results.right_hand_landmarks.landmark[4].x)
            yTpos = winY * results.right_hand_landmarks.landmark[4].y

            # print("XIP: ", xIPos, " YIP: ", yIPos)
            # print("XT: ", xTpos, " YT: ", yTpos)
            
            distanceIT = getDistance(xIPos, yIPos, xTpos, yTpos)

            #if xIPos > xStart and xIPos < xEnd and yIPos > yStart and yIPos < yEnd, and give some tolerance:
            if xIPos > (xStart - winX//15) and xIPos < (xEnd + winX //15) and yIPos > (yStart - winY//15) and yIPos < (yEnd + winY//15):
                
                # calculate percentage
                xIPect = (xIPos - xStart)/ rectWidth
                yIPect = (yIPos - yStart)/ rectHeight

                xTPect = (xTpos - xStart)/ rectWidth
                yTPect = (yTpos - yStart)/ rectHeight

                # bunch of stupid codes
                if xIPect < 0:
                    xIPect = 0
                elif xIPect > 1:
                    xIPect = 1
                
                if yIPect < 0:
                    yIPect = 0
                elif yIPect > 1:
                    yIPect = 1
                
                if xTPect < 0:
                    xTPect = 0
                elif xTPect > 1:
                    xTPect = 1
                
                if yTPect < 0:
                    yTPect = 0
                elif yTPect > 1:
                    yTPect = 1

                print("XIPercent: ", xIPect, " YIPercent: ", yIPect)
                
                # Transfer small coordinate to big screen
                xSIPos = xIPect * scrX
                ySIPos = yIPect * scrY

                #print(distanceIT)
                if  distanceIT >= 100:
                    #print("Yes")
                    pyautogui.moveTo(xSIPos, ySIPos)

                
                elif distanceIT < 100:
                    xSTpos = xTPect * scrX
                    ySTpos = yTPect * scrY
                    print(distanceIT)
                    pyautogui.moveTo((xSIPos + xSTpos)/2, (ySIPos + ySTpos)/2)

                    if distanceIT < 15:
                        #pyautogui.doubleClick()
                        print("Double Click")
                        time.sleep(0.5)

        
        image = cv2.flip(image, 1)
        cv2.imshow("image", image)

        if cv2.waitKey(5) & 0xFF == 27:
            break


cap.release()
