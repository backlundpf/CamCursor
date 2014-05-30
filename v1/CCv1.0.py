# CamCursor.py
#
# Control the cursor by using the webcam to monitor a surface for a laser pointer.
#
# v 1.0
# Updated laser location using NumPy
#
# Dependencies: VideoCapture, Image, numpy
#
# Author: Peter Backlund
# Date: 22/4/2014 (dd/mm/yyyy)

#****************************************************************#
# imports
#****************************************************************#
from VideoCapture import Device
import Image
import ctypes
import threading, time
import webbrowser
import numpy as np

#****************************************************************#
# global variables
#****************************************************************#
global resx, resy
resx = 640
resy = 480
global cam
cam = Device()
# Manually set resolution for now, figure out how to find disp res.
cam.setResolution(resx,resy)
#cam.displayCapturePinProperties()

# we need the x,y blocksize
global blockSize

global curPos, lastPos
lastPos = [0, 0]

global dim
dim = [[0, 0], [0, 0], [0, 0], [0, 0]]
global cornCnt
cornCnt = 0

#****************************************************************#
# functions
#****************************************************************#

# setBlk()
#
# using dim set the blocksize
def setBlk():
    global blockSize
    xsize = 1280/(dim[1][0]-dim[0][0])
    ysize = 720/(dim[3][1]-dim[0][1])
    blockSize = [xsize, ysize]

# getShot()
#
# Take a picture using the webcam
def getShot():
    print 'getShot'
    global cam

    cam.saveSnapshot('..\image\current.jpg')
    #return cam.getImage()

# openCurrent()
#
# Open and return the picture in the current directory
# labeled current.jpg
def openCurrent():
    print 'openCurrent'
    im = Image.open('..\image\current.jpg')
    webbrowser.open('..\image\current.jpg')
    return im.load()

# getCorn()
#
# This function is called four times to
# determine the corners of the screen.
def getCorn():
    global cornCnt, dim
    print "corner" + str(cornCnt)
    raw_input("Press enter")
    dim[cornCnt] = locPos()
    cornCnt += 1


# locPos(image)
#
# Use this function to find the coordinates of the highest
# red intensity in an image.
def locPos():
    print 'locPos'
    global resx, resy
    global cam
    #take a picture
    im = cam.getImage().load()
    #im = im.load()
    #getShot()
    #im = openCurrent()
    #webbrowser.open('..\image\current.jpg')

    #print 'imsize' + im.size
    # assume laser in in the center of screen
    max = [320, 290, 50]
    #print max
    #----------------------------#
    for x in range(resx):
        for y in range(resy):
            if im[x, y][0] > max[2] and im[x, y][1] < 100 and im[x, y][2] < 100:
                max[0] = x
                max[1] = y
                max[2] = im[x, y][0]
    #----------------------------#

    return max[0:2]
    
def getDim():
    # The user should first point the laser pointer in the top right
    # corner of the screen, then hit enter while still holding the laser
    # pointer. Proceed to each corner in a clockwise order.

    global cornCnt

    while cornCnt < 4:
        getCorn()
    # let's put dots at the vertices
    getShot()
    im = Image.open('..\image\current.jpg')
    #im = openCurrent()

    for vert in dim:
        px = vert[0]
        py = vert[1]
        print "vertical: " + str(vert)
        for x in range(px-3, px+3, 1):
            for y in range(py-3, py+3, 1):
                im.putpixel((x,y), (256, 0, 0))
    #----------------------------#

    im.save('verts.jpg')
    webbrowser.open('verts.jpg')
    print 'saved'

    return dim

# moveCursor(coords)
#
# Convert the given coords to x, y coordinates on the screen and
# move the cursor there.
def moveCursor(coords):
    global dim
    global blockSize
    # screen res is 1280x720
    screenX = (coords[0]-dim[0][0])*blockSize[0]
    screenY = (coords[1]-dim[0][1])*blockSize[1]
    #win32api.SetCursorPos((screenX, screenY))
    ctypes.windll.user32.SetCursorPos(screenX, screenY)

# checkScreen()
#
# This function should be called routinely. If the laser pointer is
# detected move the mouse and call the function again. Otherwise wait
# wTime.
def checkScreen():
    global curPos, lastPos
    # set acceptable range for cursor movement
    rad = 10
    # set the interval we want this function to be called on.
    wTime = 1
    # call locPos to find current laser position
    curPos = locPos()

    # if the current laser position is close enough to the last known position
    if abs(curPos[0]-lastPos[0]) < rad and abs(curPos[1]-lastPos[1]) < rad:
        # move the cursor to the new coordinates
        moveCursor(curPos)
        lastPos = curPos
        wTime = 0.1

    # set a timer to call this function again.
    threading.Timer(wTime, checkScreen).start()



def main():
    # First, determine the screen dimensions by pointing the laser
    # in each corner and hitting enter. Should return a 4x2 array.
    dim = getDim()

    # set the increments the cursor will move by
    setBlk()
    # periodically see if there is a laser pointer present.
    checkScreen()
    print dim

    #locPos()
if __name__ == "__main__":
    main()
