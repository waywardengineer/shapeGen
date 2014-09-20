from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
minLineSize = 0.1
class DataWrapper():
	def __init__(self, dictObj):
		self._dictObj = dictObj
	def __getattr__(self, item):
		if item not in ['_dictObj']:
			if item in self._dictObj.keys():
				data = self._dictObj[item]
				if isinstance(data, dict):
					return DataWrapper(self._dictObj[item])
				else:
					return data
		return False

class Shape(object):
	def __init__(self, params):
		self.params = params
		self.subShapes = []
		self.error = False
		self.makeDataWrappers()
		self.parent = False
		self.timesCopied = 0
		self.transformations = []
		self.derivedParams = []
	def build(self):
		self.processParams()
		for subShape in self.subShapes:
			subShape.build()

	def makeDataWrappers(self):
		self.p = DataWrapper(self.params)
		for subShape in self.subShapes:
			subShape.makeDataWrappers()

	def deleteDataWrappers(self):
		self.p = False
		for subShape in self.subShapes:
			subShape.deleteDataWrappers()

	def addToDrawing(self, drawing):
		for subShape in self.subShapes:
			subShape.addToDrawing(drawing)

	def transform(self, angle = 0, distance = (0, 0)):
		self.transformations.append((angle, distance))
		for subShape in self.subShapes:
			subShape.transform(angle, distance)

	def applyTransforms(self):
		pass


	def getCopy(self, topLevelCopy = True):
		newCopy = copy(self)
		for attr in ['params', 'transformations', 'timesCopied', 'derivedParams']:
			setattr(newCopy, attr, deepcopy(getattr(self, attr)))
		newCopy.makeDataWrappers()
		newCopy.subShapes = [s.getCopy(False) for s in self.subShapes]
		for shape in newCopy.subShapes:
			shape.setParent(newCopy)
		if self.p.id and topLevelCopy:
			self.timesCopied += 1
			newCopy.params['id'] += str(self.timesCopied)
		return newCopy

	def getTransformedCopy(self, angle = 0, distance = (0, 0)):
		newCopy = self.getCopy()
		newCopy.transform(angle, distance)
		return newCopy

	def getParamDirectory(self):
		data = []
		for subShape in self.subShapes:
			data += subShape.getParamDirectory()
		if self.p.id:
			for item in data:
				item['id'] = self.p.id + '.' + item['id']
			if self.p.changeableParams:
				changeableParamsData = {k : self.params[k] for k in self.p.changeableParams}
			else:
				changeableParamsData = {}
			data.append({'id' : self.p.id, 'changeableParams' : changeableParamsData, 'object' : self})
		return data

	def updateParam(self, param, value):
		self.params[param] = value

	def processParams(self):
		for paramKey in self.params.keys():
			if paramKey not in ['id', 'reverse'] and isinstance(self.params[paramKey], basestring):
				self.derivedParams.append(paramKey)
				param = self.params[paramKey]
				foundMathOperation = False
				for operator in ['+', '-', '/', '*']:
					if operator in param:
						foundMathOperation = operator
						(param, operand) = param.split(operator)
				identifier = param.split('.')
				param = self.passParamSearchUpward(len(identifier) - 2, identifier)
				if param is None:
					raise Exception('Error looking up param ' + '.'.join(identifier))
				if foundMathOperation:
					operand = float(operand)
					if foundMathOperation == '+':
						param += operand
					elif foundMathOperation == '-':
						param -= operand
					elif foundMathOperation == '/':
						param /= operand
					elif foundMathOperation == '*':
						param *= operand
				self.params[paramKey] = param
	def passParamSearchUpward(self, levelsLeft, *searchParams):
		if levelsLeft > 0:
			if self.parent:
				return self.parent.passParamSearchUpward(levelsLeft - 1, *searchParams)
		else:
			return self.doParamSearch(*searchParams)

	def doParamSearch(self, identifier):
		print identifier
		id = identifier.pop(0)
		print self.p.id
		
		if id in [self.p.id, 'any']:
			if len(identifier) == 1:
				if identifier[0] in self.params.keys():
					print self.params[identifier[0]]
					return self.params[identifier[0]]
			else:
				for shape in self.subShapes:
					result = shape.doParamSearch(identifier)
					if result is not None:
						return result
		return None

	def setParent(self, parent):
		self.parent = parent

class Circle(Shape):
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing)
		circle = dxf.circle(self.p.radius, self.p.centerPoint, layer = '0')
		drawing.add(circle)
	def applyTransforms(self):
		for transform in self.transformations:
			(angle, distance) = transform
			for key in ['centerPoint']:
				if key in self.params.keys() and key not in self.derivedParams:
					self.params[key] = transformPoint(self.params[key], angle, distance)
	def build(self, *args): 
		Shape.build(self, *args)
		self.applyTransforms()

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

	def build(self, *args): 
		Shape.build(self, *args)
		self.applyTransforms()

	def applyTransforms(self):
		for transform in self.transformations:
			(angle, distance) = transform
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
	def __init__(self, id, *shapes):
		Shape.__init__(self, {'id' : id})
		self.subShapes = [shape for shape in shapes]
		if self.p.id:
			for shape in self.subShapes:
				shape.setParent(self)


class Spiral(Shape):
	def getRadius(self, angleFromStart):
		b = 0.0053468
		radius = self.params['scaleFactor'] * pow(e, b * self.params['growthFactorAdjustment'] * angleFromStart)
		return radius

	def build(self, *args): 
		Shape.build(self, *args)
		self.applyTransforms()
	
	def addToDrawing(self, drawing):
		angleFromStart = 0
		points = []
		if self.p.reverse:
			direction = -1
		else:
			direction = 1
		while angleFromStart <= self.p.angleRange:
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
			
	def applyTransforms(self):
		for transform in self.transformations:
			(angle, distance) = transform
			if 'startPoint' in self.params.keys() and 'startPoint' not in self.derivedParams:
				self.params['startPoint'] = (self.params['startPoint'][0] + distance[0], self.params['startPoint'][1] + distance[1])
			if 'startAngle' not in self.derivedParams:
				self.params['startAngle'] += angle

class Arc(Shape):
	def build(self, *args): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
		Shape.build(self, *args)
		self.applyTransforms()
		if listContains(['startPoint', 'startAngle', 'endPoint'], self.params.keys()):
			startPoint = self.p.startPoint
			startAngleRads = radians(self.p.startAngle)
			endPoint = self.p.endPoint
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
			startPoint = self.p.startPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
			self.params['centerPoint'] = centerPoint
			self.params['endPoint'] = endPoint
		elif listContains(['centerPoint', 'radius', 'startAngle', 'endAngle'], self.params.keys()):
			centerPoint = self.p.centerPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			self.params['startPoint'] = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.params['endPoint'] = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
		else:
			self.error = 'No valid combination of arc data'
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing) 
		if not self.error:
			if self.p.reverse:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['endAngle'], self.params['startAngle'], layer = '0')
			else:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['startAngle'], self.params['endAngle'], layer = '0')
			drawing.add(arc)

	def applyTransforms(self):
		for transform in self.transformations:
			(angle, distance) = transform
			for key in ['startPoint', 'endPoint', 'centerPoint']:
				if key in self.params.keys() and key not in self.derivedParams:
					self.params[key] = transformPoint(self.params[key], angle, distance)
			for key in ['startAngle', 'endAngle']:
				if key in self.params.keys() and key not in self.derivedParams:
					self.params[key] += angle
		

class HolesOnArcChain(Shape):
	def __init__(self, arcChain, *args):
		Shape.__init__(self, *args)
		self.subShapes = [arcChain]
	def build(self, *args):
		Shape.build(self, *args)
		self.applyTransforms()
		def calculateNextRadius(angleOnArc):
			arcLengthUsed = sum([arcLengths[i] for i in range(currentArcIndex)])
			arcLengthUsed += (angleOnArc / arcAngleDiffs[currentArcIndex]) * arcLengths[currentArcIndex]
			interval = totalArcLength / (len(self.p.holeRadii) - 1.)
			angle = (pi / 2) * ((arcLengthUsed % interval) / interval)
			radiusIndex = int(arcLengthUsed // interval)
			if (radiusIndex + 1) >= len(self.p.holeRadii):
				nextRadiusIndex = radiusIndex
			else:
				nextRadiusIndex = radiusIndex + 1
			radius = self.p.holeRadii[radiusIndex] + sin(angle) * (self.p.holeRadii[nextRadiusIndex] - self.p.holeRadii[radiusIndex])
			return radius

		def calculateNextAngleIncrement(distanceToNextHole):
			angleIncrement = 2 * degrees(asin(distanceToNextHole / (2 * arcList[currentArcIndex].p.radius)))
			return angleIncrement

		def getCenterPoint(arcIndex, angleOnArc):
			arc = arcList[arcIndex]
			if arc.p.reverse:
				angle = arc.p.startAngle - angleOnArc
			else:
				angle = arc.p.startAngle + angleOnArc
			vector = polarToCartesian((angle, arc.p.radius))
			return (vector[0] + arc.p.centerPoint[0], vector[1] + arc.p.centerPoint[1])
		def transitionToNextArc(lastCenterPoint, targetDistanceToNextHole, newArcIndex):
			angle = 0
			error = 100
			lastError = 200
			while error > 5 and error < lastError:
				lastError = error
				newCenterPoint = getCenterPoint(newArcIndex, angle)
				distanceToNextHole = hypot(lastCenterPoint[0] - newCenterPoint[0], lastCenterPoint[1] - newCenterPoint[1])
				error = 100. * (targetDistanceToNextHole - distanceToNextHole) / targetDistanceToNextHole
				angle += 1
			return angle
		arcList = self.subShapes[0].subShapes
		arcLengths = []
		arcAngleDiffs = []
		for arc in arcList:
			if arc.p.reverse:
				angleDiff = arc.p.startAngle - arc.p.endAngle
			else:
				angleDiff = arc.p.endAngle - arc.p.startAngle
			angleDiff = (angleDiff + 720) % 360
			arcAngleDiffs.append(angleDiff)
			arcLengths.append(arc.p.radius * 2 * pi * angleDiff / 360.)
		totalArcLength = sum(arcLengths)
		currentArcIndex = 0
		currentAngleOnArc = 0
		nextRadius = self.p.holeRadii[0]
		while currentArcIndex < len(arcList):
			while currentAngleOnArc < arcAngleDiffs[currentArcIndex]:
				radius = nextRadius
				centerPoint = getCenterPoint(currentArcIndex, currentAngleOnArc)
				self.subShapes.append(Circle({
					'centerPoint' : centerPoint,
					'radius' : radius
				}))
				distanceToNextHoleEstimate = self.p.holeDistance + (radius + nextRadius)
				angleIncrementEstimate = calculateNextAngleIncrement(distanceToNextHoleEstimate)
				nextRadius = calculateNextRadius(currentAngleOnArc + angleIncrementEstimate)
				distanceToNextHole = self.p.holeDistance + (radius + nextRadius)
				angleIncrement = calculateNextAngleIncrement(distanceToNextHole)
				currentAngleOnArc += angleIncrement
			currentArcIndex += 1
			if currentArcIndex < len(arcList):
				currentAngleOnArc = transitionToNextArc(centerPoint, distanceToNextHole, currentArcIndex)
	def addToDrawing(self, drawing):
		self.subShapes.pop(0)
		Shape.addToDrawing(self, drawing)

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

