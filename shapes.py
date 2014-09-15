from math import sin, cos, radians, pi, atan2, hypot, e, degrees
from copy import deepcopy
from dxfwrite import DXFEngine as dxf


class Shape(object):
	def __init__(self, params):
		self.params = params
		self.subShapes = []
		self.error = False
	def addToDrawing(self, drawing):
		for subShape in self.subShapes:
			subShape.addToDrawing(drawing)
	def transform(self, angle = 0, distance = (0, 0)):
		for subShape in self.subShapes:
			subShape.transform(angle, distance)
	def getCopy(self):
		return deepcopy(self)
	def getTransformedCopy(self, angle = 0, distance = (0, 0)):
		newCopy = self.getCopy()
		newCopy.transform(angle, distance)
		return newCopy


class Circle(Shape):
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing)
		circle = dxf.circle(self.params['radius'], self.params['centerPoint'], layer = '0')
		drawing.add(circle)
	def transform(self, angle = 0, distance = (0, 0)):
		Shape.transform(self, angle, distance)
		self.params['centerPoint'] = transformPoint(self.params['centerPoint'], angle, distance)


class BezCurve(Shape):
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing) #params: {'points' : [((x, y), angle, (strengthIn, strengthOut))]}
		curve = dxf.bezier(layer = '0')
		points = self.params['points']
		vectors = self.makeVectors(self.params['points'][0])
		curve.start(points[0][0], vectors[1])
		for i in range(1, len(points)):
			strengthIn = points[i][2][0]
			strengthOut = points[i][2][1]
			angle = radians(points[i][1])
			vectors = self.makeVectors(self.params['points'][i])
			segments = int(hypot(points[i-1][0][0] - points[i][0][0], points[i-1][0][1] - points[i][0][1]) / minLineSize) + 1
			curve.append(points[i][0], vectors[0], vectors[1], segments)
		drawing.add(curve)

	def makeVectors(self, point):
		angle = radians(point[1])
		unitVectorOut = (cos(angle), sin(angle))
		unitVectorIn = (-unitVectorOut[0], -unitVectorOut[1])
		strengthIn = point[2][0]
		strengthOut = point[2][1]
		vectorOut = (unitVectorOut[0] * strengthOut, unitVectorOut[1] * strengthOut)
		vectorIn = (unitVectorIn[0] * strengthIn, unitVectorIn[1] * strengthIn)
		return (vectorIn, vectorOut)

	def transform(self, angle = 0, distance = (0, 0)):
		Shape.transform(self, angle, distance)
		newPoints = []
		for point in self.params['points']:
			newPoint = (
				transformPoint(point[0], angle, distance),
				point[1] + angle,
				point[2]
			)
			newPoints.append(newPoint)
		self.params['points'] = newPoints


class ShapeGroup(Shape):
	def __init__(self, *shapes):
		self.subShapes = [shape for shape in shapes]

class Spiral(Shape):
	def getRadius(self, angleFromStart):
		b = 0.0053468
		radius = self.params['scaleFactor'] * pow(e, b * self.params['growthFactorAdjustment'] * angleFromStart)
		return radius

	def getFactoredPointList(self, factor):
		pass
	
	def addToDrawing(self, drawing):
		angleFromStart = 0
		points = []
		if 'reverse' in self.params.keys() and self.params['reverse']:
			direction = -1
		else:
			direction = 1
		while angleFromStart <= self.params['angleRange']:
			radius = self.getRadius(angleFromStart)
			if not ('minRadius' in self.params.keys() and radius < self.params['minRadius']):
				pointInPolar = (self.params['startAngle'] + direction * angleFromStart, radius)
				point = polarToCartesian(pointInPolar)
				if 'startPoint' in self.params.keys():
					point = (point[0] + self.params['startPoint'][0], point[1] + self.params['startPoint'][1])
				points.append(point)
			angleFromStart += minLineSize / (sin(radians(1)) * radius)
		for i in range(1, len(points)):
			line = dxf.line(points[i-1], points[i], layer = '0')
			drawing.add(line)
			
	def transform(self, angle = 0, distance = (0, 0)):
		Shape.transform(self, angle, distance)
		if 'startPoint' in self.params.keys():
			self.params['startPoint'] = (self.params['startPoint'][0] + distance[0], self.params['startPoint'][1] + distance[1])
		else:
			self.params['startPoint'] = (distance[0], distance[1])
		self.params['startAngle'] += angle

class Arc(Shape):
	def __init__(self, params): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
		Shape.__init__(self, params)
		if listContains(['startPoint', 'startAngle', 'endPoint'], self.params.keys()):
			startPoint = params['startPoint']
			startAngleRads = radians(params['startAngle'])
			endPoint = params['endPoint']
			rightTriangleCornerOffset = ((endPoint[0] - startPoint[0]) / 2., (endPoint[1] - startPoint[1]) / 2.)
			adjacentAngleRads = atan2(rightTriangleCornerOffset[1], rightTriangleCornerOffset[0])
			triangleAngleRads = startAngleRads - adjacentAngleRads
			radius = hypot(*rightTriangleCornerOffset) / abs(cos(triangleAngleRads))
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endAngleRads = atan2(endPoint[1] - centerPoint[1], endPoint[0] - centerPoint[0])
			centerEndDist = hypot(centerPoint[0] - endPoint[0], centerPoint[1] - endPoint[1])
			if not (radius * 0.95 < centerEndDist and radius * 1.05 > centerEndDist):
				startAngleRads += pi
				triangleAngleRads = startAngleRads - adjacentAngleRads
				radius = hypot(*rightTriangleCornerOffset) / abs(cos(triangleAngleRads))
				centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
				endAngleRads = atan2(endPoint[1] - centerPoint[1], endPoint[0] - centerPoint[0])
				self.params['startAngle'] += 180
			self.params['radius'] = radius
			self.params['centerPoint'] = centerPoint
			self.params['endAngle'] = degrees(endAngleRads)
		elif listContains(['startPoint', 'startAngle', 'radius', 'endAngle'], self.params.keys()):
			startPoint = params['startPoint']
			startAngleRads = radians(params['startAngle'])
			endAngleRads = radians(params['endAngle'])
			radius = params['radius']
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
			self.params['centerPoint'] = centerPoint
			self.params['endPoint'] = endPoint
		elif listContains(['centerPoint', 'radius', 'startAngle', 'endAngle'], self.params.keys()):
			centerPoint = self.params['centerPoint']
			startAngleRads = radians(params['startAngle'])
			endAngleRads = radians(params['endAngle'])
			radius = self.params['radius']
			self.params['startPoint'] = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.params['endPoint'] = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
		else:
			self.error = 'No valid combination of arc data'
		print self.params

	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing) 
		if not self.error:
			if 'reverse' in self.params.keys() and self.params['reverse']:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['endAngle'], self.params['startAngle'], layer = '0')
			else:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['startAngle'], self.params['endAngle'], layer = '0')
			drawing.add(arc)

	def transform(self, angle = 0, distance = (0, 0)):
		Shape.transform(self, angle, distance)
		for key in ['startPoint', 'endPoint', 'centerPoint']:
			if key in self.params.keys():
				self.params[key] = transformPoint(self.params[key], angle, distance)
		for key in ['startAngle', 'endAngle']:
			if key in self.params.keys():
				self.params[key] += angle
		
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

minLineSize = 0.05
drawing = dxf.drawing('test.dxf')
# circle = Circle({'center' : (5, 0), 'radius' : 0.75})
curve = BezCurve({'points' : [
	((0,0), 210, (1,1)), 
	((-1,5), 150, (1,5)),
	((-6,-3), 90, (5,1))
]})
# subGroup = ShapeGroup(circle, curve)
# mainGroup = ShapeGroup(subGroup, subGroup.getTransformedCopy(angle=120, distance=(5,0)), subGroup.getTransformedCopy(angle=240, distance=(10,0)))
# mainGroup.addToDrawing(drawing)
# spiral1 = Spiral({'startAngle' : 60, 'angleRange' : 720, 'scaleFactor' : 0.9, 'growthFactorAdjustment' : 1})
# spiral2 = Spiral({'startAngle' : 60, 'angleRange' : 720, 'scaleFactor' : 1, 'growthFactorAdjustment' : 1})
# spiral4 = Spiral({'startAngle' : 60, 'angleRange' : 720, 'scaleFactor' : 1, 'growthFactorAdjustment' : 1, 'reverse' : True})
# spiral3 = Spiral({'startAngle' : 60, 'angleRange' : 720, 'scaleFactor' : 1.1, 'growthFactorAdjustment' : 1})
# mainGroup = ShapeGroup(spiral1, spiral2, spiral3)
arc1 = Arc({
	'startPoint' : (0, 0),
	'startAngle' : 240,
	'endAngle' : 350,
	'radius' : 2
})
arc2 = Arc({
	'startPoint' : arc1.params['endPoint'],
	'startAngle' : arc1.params['endAngle'] + 180,
	'radius' : 8,
	'endAngle' : 60,
	'reverse' : True
})
arcs = ShapeGroup(arc1, arc2)
arcs2 = arcs.getTransformedCopy(angle = -20)
arcsGroup = ShapeGroup(
	arcs, arcs2
)
arc3 = Arc({
	'startPoint' : arcs2.subShapes[1].params['endPoint'],
	'startAngle' : arcs2.subShapes[1].params['endAngle'] + 180,
	'radius' : 8,
	'endAngle' : 300,
	'reverse' : False
})
armGroup = ShapeGroup(arcsGroup, arc3)
armGroup.transform(distance = (-(arc3.params['endPoint'][0] + 2), -(arc3.params['endPoint'][1] + 1)))
mainGroup = ShapeGroup(armGroup, armGroup.getTransformedCopy(angle = 120),  armGroup.getTransformedCopy(angle = 240))
mainGroup.addToDrawing(drawing)
drawing.save()
