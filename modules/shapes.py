from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
minLineSize = 0.1


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

def interpolate(value, pair1, pair2):
	return pair1[1] + (pair2[1] - pair1[1]) * ((value - pair1[0]) / (pair2[0] - pair1[0]))

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
		self.transforms = []
		self.derivedParams = []

	def build(self):
		for subShape in self.subShapes:
			subShape.build()
		self.processParams()
		self.applyTransforms()

	def makeDataWrappers(self):
		self.p = DataWrapper(self.params)
		for subShape in self.subShapes:
			subShape.makeDataWrappers()

	def addToDrawing(self, drawing):
		if not self.p.dontRenderSubShapes:
			for subShape in self.subShapes:
				subShape.addToDrawing(drawing)

	def transform(self, angle = 0, distance = (0, 0)):
		self.transforms.append((angle, distance))
		# for subShape in self.subShapes:
			# subShape.transform(angle, distance)


	def applyTransforms(self):
		for transform in self.transforms:
			for subShape in self.subShapes:
				subShape.transform(*transform)
		for subShape in self.subShapes:
			subShape.applyTransforms()
		self.transforms = []

	def getCopy(self, topLevelCopy = True):
		newCopy = copy(self)
		for attr in ['params', 'transforms', 'timesCopied', 'derivedParams']:
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
		
	def prepareParamForMathOperation(self, param):
		operator = False
		operand = False
		for operatorToCheck in ['/', '*', '+', '-']:
			if (not operator) and operatorToCheck in param:
				operator = operatorToCheck
				(param, operand) = param.split(operatorToCheck)
		return (param, operator, operand)
	def doParamMathOperation(self, param, operator, operand):
		if operator:
			if isinstance(param, tuple):
				param = (self.doParamMathOperation(param[0], operator, operand), self.doParamMathOperation(param[1], operator, operand))
			else:
				operand = float(operand)
				if operator == '+':
					param += operand
				elif operator == '-':
					param -= operand
				elif operator == '/':
					param /= operand
				elif operator == '*':
					param *= operand
		return param
	def processParams(self):
		def processListOfParams(paramIds):
			for paramId in paramIds:
				if paramId not in ['id', 'reverse', 'changeableParams'] and isinstance(self.params[paramId], basestring):
					self.derivedParams.append(paramId)
					result = self.prepareParamForMathOperation(self.params[paramId])
					identifier = result[0].split('.')
					if len(identifier) == 2:
						if paramId not in selfReferencedParamKeys:
							selfReferencedParamKeys.append(paramId)
							continue
					param = self.passParamSearchUpward(len(identifier) - 2, identifier)
					if param is None:
						raise Exception('Error looking up param ' + '.'.join(identifier))
					param = self.doParamMathOperation(param, result[1], result[2])
					self.params[paramId] = param
		selfReferencedParamKeys = []
		processListOfParams(self.params.keys())
		processListOfParams(selfReferencedParamKeys)
		for i in range(len(self.transforms)):
			changed = False
			newTransform = [self.transforms[i][0], self.transforms[i][1]] 
			for j in range(2):
				if isinstance(self.transforms[i][j], basestring):
					result = self.prepareParamForMathOperation(self.transforms[i][j])
					identifier = result[0].split('.')
					param = self.doParamSearch(identifier)
					if param is None:
						print self.params
						print identifier
						raise Exception('Error looking up param ' + '.'.join(identifier))
					newTransform[j] = self.doParamMathOperation(param, result[1], result[2])
					changed = True
			if changed:
				self.transforms[i] = (newTransform[0], newTransform[1])

	def passParamSearchUpward(self, levelsLeft, identifier):
		if levelsLeft > 0:
			if self.parent:
				return self.parent.passParamSearchUpward(levelsLeft - 1, identifier)
		else:
			if len(identifier) > 0:
				return self.doParamSearch(identifier)
		return None

	def doParamSearch(self, identifier):
		identifier = deepcopy(identifier)
		print ''
		print self.params
		print identifier
		print ''
		
		if len(identifier) > 0:
			id = identifier.pop(0)
			if id in [self.p.id, 'any']:
				if len(identifier) == 1:
					if identifier[0] in self.params.keys():
						return self.params[identifier[0]]
				elif len(identifier) > 1:
					for shape in self.subShapes:
						result = shape.doParamSearch(identifier)
						if result is not None:
							return result
		return None

	def setParent(self, parent):
		self.parent = parent

	def addSubShape(self, shape):
		self.subShapes.append(shape)
		shape.setParent(self)

class ShapeGroup(Shape):
	def __init__(self, id, *shapes):
		Shape.__init__(self, {'id' : id})
		self.subShapes = [shape for shape in shapes]
		if self.p.id:
			for shape in self.subShapes:
				shape.setParent(self)


class Circle(Shape):
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing)
		circle = dxf.circle(self.p.radius, self.p.centerPoint, layer = '0')
		drawing.add(circle)
	def applyTransforms(self):
		transforms = deepcopy(self.transforms)
		Shape.applyTransforms(self)
		for transform in transforms:
			(angle, distance) = transform
			for key in ['centerPoint']:
				if key in self.params.keys() and key not in self.derivedParams:
					self.params[key] = transformPoint(self.params[key], angle, distance)


class Arc(Shape):
	def build(self, *args): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
		Shape.build(self, *args)
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
			print self.params
			raise Exception('No valid combination of arc data')
		if self.p.reverse:
			angleSpan = self.p.startAngle - self.p.endAngle
		else:
			angleSpan = self.p.endAngle - self.p.startAngle
		angleSpan = (angleSpan + 720) % 360
		self.params['angleSpan'] = angleSpan
		self.params['arcLength'] = self.p.radius * 2 * pi * angleSpan / 360.


	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing) 
		if not self.error:
			if self.p.reverse:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['endAngle'], self.params['startAngle'], layer = '0')
			else:
				arc = dxf.arc(self.params['radius'], self.params['centerPoint'], self.params['startAngle'], self.params['endAngle'], layer = '0')
			drawing.add(arc)

	def applyTransforms(self):
		transforms = deepcopy(self.transforms)
		Shape.applyTransforms(self)
		for transform in transforms:
			(angle, distance) = transform
			for key in ['startPoint', 'endPoint', 'centerPoint']:
				if key in self.params.keys():
					self.params[key] = transformPoint(self.params[key], angle, distance)
			for key in ['startAngle', 'endAngle']:
				if key in self.params.keys():
					self.params[key] += angle

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

	def applyTransforms(self):
		transforms = deepcopy(self.transforms)
		Shape.applyTransforms(self)
		for transform in transforms:
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

class Spiral(Shape):
	def getRadius(self, angleFromStart):
		b = 0.0053468
		radius = self.params['scaleFactor'] * pow(e, b * self.params['growthFactorAdjustment'] * angleFromStart)
		return radius

	def build(self, *args): 
		Shape.build(self, *args)
		angleFromStart = 0
		self.points = []
		self.arcLengthLookup = []
		if self.p.reverse:
			direction = -1
		else:
			direction = 1
		arcLength = 0
		while angleFromStart <= self.p.angleSpan:
			radius = self.getRadius(angleFromStart)
			if not ('minRadius' in self.params.keys() and radius < self.params['minRadius']):
				pointInPolar = (self.params['startAngle'] + direction * angleFromStart, radius)
				point = addVectors(polarToCartesian(pointInPolar), self.p.centerPoint)
				if len(self.points) > 0:
					arcLength += distanceBetween(point, self.points[-1])
					self.arcLengthLookup.append((angleFromStart, arcLength))
				self.points.append(point)
			angleFromStart += minLineSize / (sin(radians(1)) * radius)
		self.params['arcLength'] = arcLength
		self.params['endPoint'] = self.points[-1]
		self.params['endAngle'] = degrees(atan2(self.points[-1][1] - self.points[-2][1], self.points[-1][0] - self.points[-2][0])) + 90
		self.params['lineStartPoint'] = self.points[0]
		self.params['lineStartAngle'] = degrees(atan2(self.points[0][1] - self.points[1][1], self.points[0][0] - self.points[1][0])) + 90

	def lookupArcLength(self, angleFromStart):
		result = [i for i, v in enumerate(self.arcLengthLookup) if v[0] < angleFromStart]
		if len(result) == 0:
			return 0
		elif len(result) == len(self.arcLengthLookup):
			return self.p.arcLength
		else:
			return interpolate(angleFromStart, self.arcLengthLookup[result[-1]], self.arcLengthLookup[result[-1] + 1]) 
			
	def addToDrawing(self, drawing):
		for i in range(1, len(self.points)):
			line = dxf.line(self.points[i-1], self.points[i], layer = '0')
			drawing.add(line)
			
	def applyTransforms(self):
		transforms = deepcopy(self.transforms)
		Shape.applyTransforms(self)
		for transform in transforms:
			(angle, distance) = transform
			if 'centerPoint' in self.params.keys():
				self.params['centerPoint'] = transformPoint(self.p.centerPoint, angle, distance)
			self.params['startAngle'] += angle

class ArcChain(ShapeGroup):
	def __init__(self, id, definitions):
		ShapeGroup.__init__(self,id)
		for i, definition in enumerate(definitions):
			if 'growthFactorAdjustment' in definition.keys():
				shape = Spiral(definition)
			else:
				shape = Arc(definition)
			self.addSubShape(shape)
			shape.updateParam('id', self.p.id + '_curve' + str(i))
			if i > 0:
				lastShape = self.subShapes[i-1]
				if shape.p.noDirectionAlternate:
					reverse = lastShape.p.reverse
				else:
					reverse = not lastShape.p.reverse
				shape.updateParam('reverse', reverse)
				if shape.__class__.__name__=='Arc':
					shape.updateParam('startPoint', '.'.join(['any', lastShape.p.id, 'endPoint']))
					if shape.p.noDirectionAlternate:
						startAngleStr = 'endAngle'
					else:
						startAngleStr = 'endAngle+180'
					shape.updateParam('startAngle', '.'.join(['any', lastShape.p.id, startAngleStr]))
			if shape.__class__.__name__=='Arc':
				if shape.p.reverse:
					endAngleStr = 'startAngle-' + str(shape.p.angleSpan)
				else:
					endAngleStr = 'startAngle+' + str(shape.p.angleSpan)
				shape.updateParam('endAngle', '.'.join([shape.p.id, endAngleStr]))
	def build(self):
		ShapeGroup.build(self)
		if self.subShapes[0].__class__.__name__ == 'Spiral':
			startPoint = self.subShapes[0].p.lineStartPoint
			startAngle = self.subShapes[0].p.lineStartAngle
		else:
			startPoint = self.subShapes[0].p.startPoint
			startAngle = self.subShapes[0].p.startAngle
		self.params['startPoint'] = startPoint
		self.params['startAngle'] = startAngle
		self.params['endPoint'] = self.subShapes[-1].p.endPoint
		self.params['endAngle'] = self.subShapes[-1].p.endAngle

class HolesOnArcChain(Shape):
	def __init__(self, arcChain, *args):
		Shape.__init__(self, *args)
		self.addSubShape(arcChain)
	def build(self, *args):
		def calculateNextRadius(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			arcLengthUsed = sum([arcs[i].p.arcLength for i in range(currentArcIndex)])
			if arc.__class__.__name__ == 'Arc':
				arcLengthUsed += (angleOnArc / arc.p.angleSpan) * arc.p.arcLength
			elif arc.__class__.__name__ == 'Spiral':
				arcLengthUsed += arc.lookupArcLength(angleOnArc)
			interval = totalArcLength / (len(self.p.holeRadii) - 1.)
			angle = (pi / 2) * ((arcLengthUsed % interval) / interval)
			radiusIndex = int(arcLengthUsed // interval)
			if (radiusIndex + 1) >= len(self.p.holeRadii):
				nextRadiusIndex = radiusIndex
			else:
				nextRadiusIndex = radiusIndex + 1
			radius = self.p.holeRadii[radiusIndex] + sin(angle) * (self.p.holeRadii[nextRadiusIndex] - self.p.holeRadii[radiusIndex])
			return radius

		def calculateNextAngleIncrement(arcIndex, angleOnArc, distanceToNextHole):
			arc = arcs[arcIndex]
			if arc.__class__.__name__ == 'Arc':
				radius = arc.p.radius
			elif arc.__class__.__name__ == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			ratio = distanceToNextHole / (2 * radius)
			if ratio > 1:
				return 180
			angleIncrement = 2 * degrees(asin(ratio))
			return angleIncrement

		def getCenterPoint(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			if arc.p.reverse:
				angle = arc.p.startAngle - angleOnArc
			else:
				angle = arc.p.startAngle + angleOnArc
			if arc.__class__.__name__ == 'Arc':
				radius = arc.p.radius
			elif arc.__class__.__name__ == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			vector = polarToCartesian((angle, radius))
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

		Shape.build(self, *args)
		arcs = self.subShapes[0].subShapes
		totalArcLength = sum(arc.p.arcLength for arc in arcs)
		currentArcIndex = 0
		currentAngleOnArc = 0
		nextRadius = self.p.holeRadii[0]
		angleIncrement = 5
		while currentArcIndex < len(arcs):
			while currentAngleOnArc < arcs[currentArcIndex].p.angleSpan:
				thisRadius = nextRadius
				centerPoint = getCenterPoint(currentArcIndex, currentAngleOnArc)
				self.subShapes.append(Circle({
					'centerPoint' : centerPoint,
					'radius' : thisRadius
				}))
				error = 100
				lastError = 200
				while error > 5 and error < lastError:
					distanceToNextHole = self.p.holeDistance + (thisRadius + nextRadius)
					angleIncrement = calculateNextAngleIncrement(currentArcIndex, currentAngleOnArc, distanceToNextHole)
					newNextRadius = calculateNextRadius(currentArcIndex, currentAngleOnArc + angleIncrement)
					lastError = error
					error = 100. * abs((nextRadius - newNextRadius) / newNextRadius)
					nextRadius = newNextRadius
				currentAngleOnArc += angleIncrement
			currentArcIndex += 1
			if currentArcIndex < len(arcs):
				currentAngleOnArc = transitionToNextArc(centerPoint, distanceToNextHole, currentArcIndex)
	def addToDrawing(self, drawing):
		self.subShapes[0].updateParam('dontRenderSubShapes', True)
		Shape.addToDrawing(self, drawing)



