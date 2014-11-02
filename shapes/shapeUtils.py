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

def interpolate(value, pair1, pair2):
	return pair1[1] + (pair2[1] - pair1[1]) * ((value - pair1[0]) / (pair2[0] - pair1[0]))

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

def linesCross(points1, points2):
	vector1 = (points1[1][0] - points1[0][0], points1[1][1] - points1[0][1])
	vector2 = (points2[1][0] - points2[0][0], points2[1][1] - points2[0][1])
	vectorBetweenStarts = (points2[0][0] - points1[0][0], points2[0][1] - points1[0][1])
	angle = degrees(atan2(vector1[1], vector1[0]))
	newVector1 = transformPoint(vector1, angle = -angle)
	newVector2 = transformPoint(vector2, angle = -angle)
	newStartPoint = transformPoint(vectorBetweenStarts, angle = -angle)
	newEndPoint = addVectors(newStartPoint, newVector2) 
	result = False
	keepChecking = True
	if (newStartPoint[1] > 0 and newEndPoint[1] > 0) or (newStartPoint[1] < 0 and newEndPoint[1] < 0):
		keepChecking = False
	if keepChecking:
		if (newStartPoint[0] > newVector1[0] and newEndPoint[0] > newVector1[0]) or (newStartPoint[0] < 0 and newEndPoint[0] < 0):
			keepChecking = False
	if keepChecking:
		line2Angle = degrees(atan2(newVector2[1], newVector2[0]))
		
	
	
	