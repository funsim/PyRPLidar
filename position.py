from scipy import ndimage
from scipy import misc
from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt

origo = np.array([0, 0, 0])
movePos = np.array([50, 0, 0])

room = misc.imread("room.png")
width = room.shape[1]
height = room.shape[0]
widthHalf = (width / 2)
heightHalf = (height / 2)

origoImagePos = origo + np.array([widthHalf, heightHalf, 0])
moveImagePos = movePos + np.array([widthHalf, heightHalf, 0])

plt.imshow(room)
plt.plot(origoImagePos[0],origoImagePos[1], marker='x', color='r')
plt.plot(moveImagePos[0],moveImagePos[1], marker='x', color='b')
#plt.show()



print "Width: " + str(width)
print "Height: " + str(height)


def calc_sample_distances(origoimage, rom):
    """
    origoimage is X, Y position of player
    rom is the size of the room, assumes squareish
    """

    angularDistances = np.zeros(360)
    angularPositionsX = np.zeros(360)
    angularPositionsY = np.zeros(360)
    relativePosX = np.zeros(360)
    relativePosY = np.zeros(360)

    for angle in range(0, 360):
        #print("Angle: " + str(angle))
        radians = np.radians(angle)
        vec = np.array([np.cos(radians), np.sin(radians), 0])
        samplePos = origoimage.copy()

        width = rom.shape[1]
        height = rom.shape[0]

        while samplePos[0] >= 0 and samplePos[0] < width and samplePos[1] >= 0 and samplePos[1] < height:
            sample = rom[samplePos[1], samplePos[0], 0]

            if sample == 0:
                dx = samplePos[0] - origoimage[0]
                dy = samplePos[1] - origoimage[1]
                dist = np.sqrt(dx**2 + dy**2)
                angularDistances[angle] = dist
                relativePosX[angle] = vec[0] * dist
                relativePosY[angle] = vec[1] * dist
                angularPositionsX[angle] = samplePos[0]
                angularPositionsY[angle] = samplePos[1]
                break

            samplePos = samplePos + vec

    #return angularPositionsX, angularPositionsY, angularDistances
    return angularDistances #relativePosX, relativePosY

def errorFunction(room, p, m):
    oad = calc_sample_distances(p, room)
    diff = (oad - m)
    error = np.sum(diff ** 2)
    return error

# Magic happens here..
#PrD = calc_sample_distances(moveImagePos, room)
OrD = calc_sample_distances(origoImagePos, room)
e = errorFunction(room, moveImagePos, OrD)
#print e

def objective(p):
    print "Trying out point ", p
    moveImagePos = np.array(list(p) + [0])
    OrD = calc_sample_distances(origoImagePos, room)
    return errorFunction(room, moveImagePos, OrD)

def derivative(p):
    p = np.array(p)
    h = 3.
    obj = objective(list(p))
    px = p + np.array([h, 0])
    py = p + np.array([0, h])
    objx = objective(list(px))
    objy = objective(list(py))

    return np.array([(objx-obj)/h, (objy-obj)/h])

print "Real answer is:", origoImagePos[:2]
minimize(objective, np.array([0, 0]), method="L-BFGS-B",
        options={"disp": True})

crash()


#plt.plot([origoImagePos[0]+ShiftPosX,origoImagePos[1]+ShiftPosY])
#plt.show()
"""
print("Vi tester")
OX, OY, OD = calc_sample_distances(origoImagePos, room)
aPX, aPY, anD = calc_sample_distances(moveImagePos, room)

plt.plot(OX, OY, 'o', color='r')
plt.plot(aPX, aPY,'x', color='b')
plt.show()
"""
#print angularDistances
print("Done")
