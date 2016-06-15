from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy

def getIntersect(point1, angle1, point2, angle2):
	vector = (point2[0] - point1[0], point2[1] - point1[1])
	vector = transformPoint(vector, -angle1)
	xDist = vector[0] + vector[1] * tan(radians(angle2 - angle1 - 90))
	vector = transformPoint((xDist, 0), angle1)
	return (addVectors(point1, vector))

def isNumeric(s):
	return all(c in "0123456789.+-" for c in s) and any(c in "0123456789" for c in s)

def listContains(searchList, list):
	match = True
	for item in searchList:
		if not item in list:
			match = False
	return match

def polarToCartesian(point):
	angle = radians(point[0])
	return (cos(angle) * point[1], sin(angle) * point[1])

def cartesianToPolar(point):
	r = hypot(point[0],  point[1])
	angle = degrees(atan2(point[1], point[0]))
	return (angle, r)

def transformPoint(point, angle = 0, distance = (0, 0)):
	point = (point[0] + distance[0], point[1] + distance[1])
	currentAngle = atan2(point[1], point[0])
	radius = hypot(*point)
	newAngle = currentAngle + radians(angle)
	point = (cos(newAngle) * radius, sin(newAngle) * radius)
	return point

def distanceBetween(point1, point2):
	return hypot(point1[0] - point2[0], point1[1] - point2[1])

def addVectors(point1, point2):
	return (point1[0] + point2[0], point1[1] + point2[1])

def subtractVectors(point1, point2):
	return (point1[0] - point2[0], point1[1] - point2[1])


def avgPoints (*points):
	result = [sum([points[i][j] for i in range(len(points))]) / len(points) for j in range(len(points[0]))] 
	return tuple(result)
	
def getEndPoint(startPoint, angle, endX = False, endY = False):
	if endX:
		xDist = endX - startPoint[0]
		yDist = xDist * tan(radians(angle))
		result = (endX, startPoint[1] + yDist)
	if endY:
		yDist = endY - startPoint[1]
		xDist = yDist / tan(radians(angle))
		result = (startPoint[0] + xDist, endY)
	return result

def getAngle(point1, point2):
	return degrees(atan2(point2[1] - point1[1], point2[0] - point1[0]))

def linesCross(L1, L2, allowance = 0, L1WidthPadding = 0.0):
	for axis in [0, 1]:
		above = True
		below = True
		for L2Point in [0, 1]:
			for L1Point in [0, 1]:
				if L1[L1Point][axis] >= L2[L2Point][axis]:
					below = False
				if L1[L1Point][axis] <= L2[L2Point][axis]:
					above = False
		if above or below:
			return False
	L1Vector = (L1[1][0] - L1[0][0], L1[1][1] - L1[0][1])
	L2Vector = (L2[1][0] - L2[0][0], L2[1][1] - L2[0][1])
	L2StartVector = (L2[0][0] - L1[0][0], L2[0][1] - L1[0][1])
	L2EndVector = (L2[1][0] - L1[0][0], L2[1][1] - L1[0][1])
	angle = degrees(atan2(L1Vector[1], L1Vector[0]))
	newL1Vector = transformPoint(L1Vector, angle = -angle)
	newL2Start = transformPoint(L2StartVector, angle = -angle)
	newL2End = transformPoint(L2EndVector, angle = -angle)
	steps = 10 #should make this bigger for bigger differences in yValue / l2 length 
	xCrossing = getXCrossing(0, newL2Start, newL2End)
	if 0 <= xCrossing <= allowance or (newL1Vector[0] - allowance) <= xCrossing <= newL1Vector[0]:
		#lines intersect and it's allowed
		return False
	for step in range(steps + 1):
		yValue = -L1WidthPadding + (float(step) / steps) * 2.0 * L1WidthPadding
		xCrossing = getXCrossing(yValue, newL2Start, newL2End)
		if xCrossing is not None and allowance <= xCrossing <= (newL1Vector[0] - allowance):
			return True
	return False

def interpolate(value, pair1, pair2): #Probably still totally fucked
	value = float(value)
	pair1 = (float(pair1[0]), float(pair1[1]))
	pair2 = (float(pair2[0]), float(pair2[1]))
	if abs(pair2[0] - pair1[0]) > 0:
		return pair1[1] + (pair2[1] - pair1[1]) * ((value - pair1[0]) / (pair2[0] - pair1[0]))
	else:
		return pair1[0]

def getXCrossing(yValue, point1, point2):
	yValue = float(yValue)
	point1 = (float(point1[0]), float(point1[1]))
	point2 = (float(point2[0]), float(point2[1]))
	if not ((point1[1] <= yValue <= point2[1]) or (point2[1] <= yValue <= point1[1])):
		return None
	if point1[0] == point2[0]:
		return point1[0]
	xRange = point2[0] - point1[0]
	yRange = point2[1] - point1[1]
	if yRange == 0:
		if point1[1] == yValue:
			return point1[0]
		return None
	yDiff = yValue - point1[1]
	xDiff = (xRange / yRange) * yDiff
	return point1[0] + xDiff

	
def getBranchEndPoints(points, offsetDistance, fromRight):
	vector = subtractVectors(points[1], points[0])
	vectorPolar = cartesianToPolar(vector)
	angle = vectorPolar[0]
	if fromRight:
		angles = [angle - 90, angle + 90]
	else:
		angles = [angle + 90, angle - 90]
	pointsOut = []
	for i in [0, 1]:
		offsetVector = polarToCartesian((angles[i], offsetDistance))
		pointsOut.append(addVectors(points[1], offsetVector))
	return pointsOut

def getOffsetIntersect(points, offsetDistance, fromRight):
	angles = []
	for i in [0, 1]:
		vector = subtractVectors(points[1 + i], points[i])
		vectorPolar = cartesianToPolar(vector)
		angles.append(vectorPolar[0])
	angles[0] += 180
	if fromRight:
		angleSubtraction = 90
	else:
		angleSubtraction = 270
	intersectAngle = ((360 + angles[0] + angles[1]) % 360) / 2
	if fromRight:
		intersectAngle += 180
	hypotAngle = (720 + angles[0] - intersectAngle - 270) % 360
	distance = offsetDistance / cos(radians(hypotAngle))
	offsetVector = polarToCartesian((intersectAngle, distance))
	return addVectors(points[1], offsetVector)

def getTreeEndPoints(points, offsetDistance, fromRight):
	angles = []
	for i in [0, 1]:
		vector = subtractVectors(points[1 + i], points[i])
		vectorPolar = cartesianToPolar(vector)
		angles.append(vectorPolar[0])
	angles[0] += 180
	intersectAngle = ((360 + angles[0] + angles[1]) % 360) / 2
	if fromRight:
		angles = [intersectAngle + 90, intersectAngle - 90]
	else:
		angles = [intersectAngle - 90, intersectAngle + 90]
	pointsOut = []
	for i in [0, 1]:
		offsetVector = polarToCartesian((angles[i], offsetDistance))
		pointsOut.append(addVectors(points[1], offsetVector))
	return pointsOut

