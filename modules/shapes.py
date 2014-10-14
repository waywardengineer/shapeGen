from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
minLineSize = 0.1
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

def interpolate(value, pair1, pair2):
	return pair1[1] + (pair2[1] - pair1[1]) * ((value - pair1[0]) / (pair2[0] - pair1[0]))

class DictWrapper():
	def __init__(self, dictObj):
		self._dictObj = dictObj
	def __getattr__(self, item):
		if item not in ['_dictObj']:
			if item in self._dictObj.keys():
				data = self._dictObj[item]
				if isinstance(data, dict):
					return DictWrapper(self._dictObj[item])
				else:
					return data
		return False
class ListWrapper():
	def __init__(self, listObj):
		self._listObj = listObj
	def __getattr__(self, item):
		if item not in ['_dictObj']:
			if len(item) == 1:
				index = ord(item) - 97
				if index < len(self._listObj):
					return self._listObj[index]

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
		self.primaryParams = params.keys()
		self.derivedParams = []
		self.params['type'] = self.__class__.__name__
		self.paramsChecked = False
		self.paramsResetting = False
		
	def build(self, topShape):
		self.topShape = topShape
		for subShape in self.subShapes:
			subShape.build(topShape)
		rejectedKeys = []
		for key in self.params.keys():
			if isinstance(self.params[key], basestring) and key not in ['id', 'type']:
				(success, result) = self.getCalculatedParam(self.params[key])
				if success:
					self.params[key] = result
				else:
					rejectedKeys.append(key)
		for key in rejectedKeys:
			(success, result) = self.getCalculatedParam(self.params[key])
			if success:
				self.params[key] = result
			else:
				raise Exception("Can't find value " + self.params[key])
		postponedTransforms = []
		postponed = False
		for i in range(len(self.transforms)):
			changed = False
			newTransform = [self.transforms[i][0], self.transforms[i][1]] 
			for j in range(2):
				if isinstance(self.transforms[i][j], basestring) and not postponed:
					(success, result) = self.getCalculatedParam(self.transforms[i][j])
					if success:
						newTransform[j] = result
						changed = True
					else:
						postponed = True
						postponedTransforms = self.transforms[i:]
						self.transforms = self.transforms[:i]
			if changed and not postponed:
				self.transforms[i] = (newTransform[0], newTransform[1])
		self.applyTransforms()
		self.transforms = postponedTransforms
		for i in range(len(self.transforms)):
			changed = False
			newTransform = [self.transforms[i][0], self.transforms[i][1]] 
			for j in range(2):
				if isinstance(self.transforms[i][j], basestring):
					(success, result) = self.getCalculatedParam(self.transforms[i][j])
					if success:
						newTransform[j] = result
						changed = True
					else:
						raise Exception("Can't find value " + self.transforms[i][j])
			if changed:
				self.transforms[i] = (newTransform[0], newTransform[1])
		self.applyTransforms()
	
	def makeDataWrappers(self):
		self.p = DictWrapper(self.params)
		self.s = ListWrapper(self.subShapes)
		for subShape in self.subShapes:
			subShape.makeDataWrappers()

	def addToDrawing(self, drawing):
		if not self.p.dontRenderSubShapes:
			for subShape in self.subShapes:
				subShape.addToDrawing(drawing)

	def transform(self, angle = 0, distance = (0, 0)):
		self.transforms.append((angle, distance))

	def applyTransforms(self):
		for transform in self.transforms:
			for subShape in self.subShapes:
				subShape.transform(*transform)
		for subShape in self.subShapes:
			subShape.applyTransforms()
		for transform in self.transforms:
			(angle, distance) = transform
			for key in ['startPoint', 'endPoint', 'centerPoint']:
				if key in self.params.keys():
					self.params[key] = transformPoint(self.params[key], angle, distance)
			for key in ['startAngle', 'endAngle', 'sweepStartAngle']:
				if key in self.params.keys():
					self.params[key] += angle
		self.transforms = []
		self.calculate()

	def getCopy(self, depth = 0, idChain = []):
		newCopy = copy(self)
		idChain = copy(idChain)
		if self.p.id:
			idChain.append(self.p.id)
			depth += 1
		for attr in ['params', 'transforms', 'timesCopied', 'primaryParams', 'derivedParams']:
			setattr(newCopy, attr, deepcopy(getattr(self, attr)))
		newCopy.subShapes = [s.getCopy(depth, idChain) for s in self.subShapes]
		newCopy.makeDataWrappers()
		for shape in newCopy.subShapes:
			shape.setParent(newCopy)
		if self.p.changeableParams:
			for paramKey in self.p.changeableParams:
				paramChain = idChain + [paramKey]
				newCopy.params[paramKey] = '.'.join(paramChain)
		if self.p.id and depth == 1:
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
		operands = [param]
		operator = False
		for operatorToCheck in ['/', '*', '+', '-']:
			if (not operator) and operatorToCheck in param:
				operator = operatorToCheck
				operands = param.split(operatorToCheck)
		return (operands, operator)

	def doParamMathOperation(self, operands, operator):
		if operator:
			if isinstance(operands[0], tuple):
				if isinstance(operands[1], tuple):
					operands[0] = (self.doParamMathOperation([operands[0][0], operands[1][0]], operator), self.doParamMathOperation([operands[0][1], operands[1][1]], operator))
				else:
					operands[0] = (self.doParamMathOperation([operands[0][0], operands[1]], operator), self.doParamMathOperation([operands[0][1], operands[1]], operator))
			else:
				operands = [float(operand) for operand in operands]
				if operator == '+':
					operands[0] += operands[1]
				elif operator == '-':
					operands[0] -= operands[1]
				elif operator == '/':
					operands[0] /= operands[1]
				elif operator == '*':
					operands[0] *= operands[1]
		return operands[0]

	def getCalculatedParam(self, param):
		success = True
		result = False
		(operands, operator) = self.prepareParamForMathOperation(param)
		for i in range(len(operands)):
			if not isNumeric(operands[i]):
				identifier = operands[i].split('.')
				param = self.doParamSearch(identifier)
				if param is None:
					success = False
				elif isinstance(param, basestring):
					success = False
				else:
					operands[i] = param
		if success:
			result = self.doParamMathOperation(operands, operator)
		return (success, result)

	def calculate(self):
		pass

	def clearParamCheckState(self):
		self.paramsChecked = False
		for shape in self.subShapes:
			shape.clearParamCheckState()
	def doParamSearch(self, identifier):
		self.topShape.clearParamCheckState()
		identifier = deepcopy(identifier)
		result = self.doParamSubsearch(identifier, False, 0)
		return result[0]

	def doParamSubsearch(self, identifier, downOnly, distance):
		if self.paramsChecked:
			return (None, distance)
		self.paramsChecked = True
		if len(identifier) == 1:
			if identifier[0] in self.params.keys():
				return (self.params[identifier[0]], distance)
			else:
				return (None, distance)
		if len(identifier) == 2:
			if identifier[0] == self.p.id:
				if identifier[1] in self.params.keys():
					return (self.params[identifier[1]], distance)
				else:
					return (None, distance)
		results = []
		if len(identifier) > 2:
			if identifier[0] == self.p.id:
				downOnly = True
				identifier = identifier[1:]
		for shape in self.subShapes:
			results.append(shape.doParamSubsearch(identifier, downOnly, distance + 1))
		if (not downOnly) and self.parent:
			results.append(self.parent.doParamSubsearch(identifier, False, distance + 1))
		bestResultDistance = distance
		bestResult = None
		for result in results:
			if result[0] is not None:
				if bestResult is None or result[1] < bestResultDistance:
					(bestResult, bestResultDistance) = result
		return (bestResult, bestResultDistance)
				

	def setParent(self, parent):
		self.parent = parent

	def addSubShape(self, shape):
		self.subShapes.append(shape)
		shape.setParent(self)

class ShapeGroup(Shape):
	def __init__(self, id, *shapes):
		Shape.__init__(self, {'id' : id})
		self.subShapes.extend([shape for shape in shapes])
		if self.p.id:
			for shape in self.subShapes:
				shape.setParent(self)
	def calculate(self):
		Shape.calculate(self)
		# self.params['startPoint'] = self.subShapes[0].p.startPoint
		# self.params['endPoint'] = self.subShapes[0].p.endPoint
		# self.params['startAngle'] = self.subShapes[0].p.startAngle
		# self.params['endAngle'] = self.subShapes[0].p.endAngle

class Circle(Shape):
	def addToDrawing(self, drawing):
		Shape.addToDrawing(self, drawing)
		circle = dxf.circle(self.p.radius, self.p.centerPoint, layer = '0')
		drawing.add(circle)


class Arc(Shape):
	def calculate(self, *args): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
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
			if not (radius * 0.95 < centerEndDist < 1.05 * radius):
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
		elif listContains(['endPoint', 'startAngle', 'radius', 'endAngle'], self.params.keys()):
			endPoint = self.p.endPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (endPoint[0] - radius * cos(endAngleRads), endPoint[1] - radius * sin(endAngleRads))
			startPoint = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.params['centerPoint'] = centerPoint
			self.params['startPoint'] = startPoint
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

	def calculate(self, *args): 
		angleFromStart = 0
		self.points = []
		self.arcLengthLookup = []
		if self.p.reverse:
			direction = -1
		else:
			direction = 1
		arcLength = 0
		while angleFromStart <= self.p.sweepAngleSpan:
			radius = self.getRadius(angleFromStart)
			if not ('minRadius' in self.params.keys() and radius < self.params['minRadius']):
				pointInPolar = (self.p.sweepStartAngle + direction * angleFromStart, radius)
				point = addVectors(polarToCartesian(pointInPolar), self.p.centerPoint)
				if len(self.points) > 0:
					arcLength += distanceBetween(point, self.points[-1])
					self.arcLengthLookup.append((angleFromStart, arcLength))
				self.points.append(point)
			angleFromStart += minLineSize / (sin(radians(1)) * radius)
		self.params['arcLength'] = arcLength
		self.params['endPoint'] = self.points[-1]
		self.params['endAngle'] = degrees(atan2(self.points[-1][1] - self.points[-2][1], self.points[-1][0] - self.points[-2][0])) + 90
		self.params['startPoint'] = self.points[0]
		self.params['startAngle'] = degrees(atan2(self.points[0][1] - self.points[1][1], self.points[0][0] - self.points[1][0])) + 90

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


class ArcChain(ShapeGroup):
	def __init__(self, id, definitions):
		ShapeGroup.__init__(self,id)
		indexForPrepends = 0
		for i, definition in enumerate(definitions):
			if 'growthFactorAdjustment' in definition.keys():
				shape = Spiral(definition)
			else:
				shape = Arc(definition)
			self.addSubShape(shape)
			shape.updateParam('id', 'arc' + str(i))
			if i > 0:
				if shape.p.prepend:
					lastShape = self.subShapes[indexForPrepends]
					indexForPrepends = i
				else:
					lastShape = self.subShapes[i-1]
				if shape.p.noDirectionAlternate:
					reverse = lastShape.p.reverse
				else:
					reverse = not lastShape.p.reverse
				shape.updateParam('reverse', reverse)
				if shape.p.type == 'Arc':
					if shape.p.noDirectionAlternate:
						angleChangeStr = ''
					else:
						angleChangeStr = '+180'
					if shape.p.prepend:
						shape.updateParam('endPoint', '.'.join([lastShape.p.id, 'startPoint']))
						shape.updateParam('endAngle', '.'.join([lastShape.p.id, 'startAngle' + angleChangeStr]))
					else:
						shape.updateParam('startPoint', '.'.join([lastShape.p.id, 'endPoint']))
						shape.updateParam('startAngle', '.'.join([lastShape.p.id, 'endAngle' + angleChangeStr]))
			if shape.p.type == 'Arc' and shape.p.angleSpan:
				if shape.p.prepend:
					if shape.p.reverse:
						startAngleStr = 'endAngle+' + str(shape.p.angleSpan)
					else:
						startAngleStr = 'endAngle-' + str(shape.p.angleSpan)
					shape.updateParam('startAngle', startAngleStr)
				else:
					if shape.p.reverse:
						endAngleStr = 'startAngle-' + str(shape.p.angleSpan)
					else:
						endAngleStr = 'startAngle+' + str(shape.p.angleSpan)
					shape.updateParam('endAngle', endAngleStr)

	def calculate(self):
		newSubShapes =  []
		for shape in self.subShapes:
			if shape.p.prepend:
				newSubShapes = [shape] + newSubShapes
			else:
				newSubShapes.append(shape)
		self.subShapes = newSubShapes
		self.params['startPoint'] = self.subShapes[0].p.startPoint
		self.params['startAngle'] = self.subShapes[0].p.startAngle
		self.params['endPoint'] = self.subShapes[-1].p.endPoint
		self.params['endAngle'] = self.subShapes[-1].p.endAngle

class HolesOnArcChain(Shape):
	def __init__(self, arcChain, *args):
		Shape.__init__(self, *args)
		self.addSubShape(arcChain)
		self.subShapes[0].updateParam('dontRenderSubShapes', True)

	def calculate(self):
		def calculateNextRadius(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			arcLengthUsed = sum([arcs[i].p.arcLength for i in range(currentArcIndex)])
			if arc.p.type == 'Arc':
				arcLengthUsed += (angleOnArc / arc.p.angleSpan) * arc.p.arcLength
			elif arc.p.type == 'Spiral':
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
			if arc.p.type == 'Arc':
				radius = arc.p.radius
			elif arc.p.type == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			ratio = distanceToNextHole / (2 * radius)
			if ratio > 1:
				return 180
			angleIncrement = 2 * degrees(asin(ratio))
			return angleIncrement

		def getCenterPoint(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			if arc.p.type == 'Spiral':
				startAngle = arc.p.sweepStartAngle
			else:
				startAngle = arc.p.startAngle
			if arc.p.reverse:
				angle = startAngle - angleOnArc
			else:
				angle = startAngle + angleOnArc
			if arc.p.type == 'Arc':
				radius = arc.p.radius
			elif arc.p.type == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			vector = polarToCartesian((angle, radius))
			return (vector[0] + arc.p.centerPoint[0], vector[1] + arc.p.centerPoint[1])

		def transitionToNextArc(lastCenterPoint, targetDistanceToNextHole, newArcIndex):
			angle = 0.
			error = 100
			lastError = 200
			while 5 < error < lastError:
				lastError = error
				newCenterPoint = getCenterPoint(newArcIndex, angle)
				distanceToNextHole = hypot(lastCenterPoint[0] - newCenterPoint[0], lastCenterPoint[1] - newCenterPoint[1])
				error = 100. * (targetDistanceToNextHole - distanceToNextHole) / targetDistanceToNextHole
				angle += 0.25
			return angle

		arcs = self.subShapes[0].subShapes
		totalArcLength = sum(arc.p.arcLength for arc in arcs)
		currentArcIndex = 0
		currentAngleOnArc = 0
		nextRadius = self.p.holeRadii[0]
		angleIncrement = 5
		while currentArcIndex < len(arcs):
			arc = arcs[currentArcIndex]
			if arc.p.type == 'Arc':
				angleSpan = arc.p.angleSpan
			elif arc.p.type == 'Spiral':
				angleSpan = arc.p.sweepAngleSpan
			while currentAngleOnArc < angleSpan:
				thisRadius = nextRadius
				centerPoint = getCenterPoint(currentArcIndex, currentAngleOnArc)
				self.subShapes.append(Circle({
					'centerPoint' : centerPoint,
					'radius' : thisRadius
				}))
				error = 100
				lastError = 200
				while 5 < error < lastError:
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

class ShapeChain(ShapeGroup):
	def __init__(self, id, *shapesAndConnections):
		ShapeGroup.__init__(self, id, *[s[0] for s in shapesAndConnections])
		self.connections = [s[1] for s in shapesAndConnections]

	def calculate(self):
		pointNames = {'e' : 'endPoint', 's' : 'startPoint'}
		for i in range(1, len(self.connections)):
			fromPointName = pointNames[self.connections[i-1][1]]
			toPointName = pointNames[self.connections[i][0]]
			fromShape = self.subShapes[i-1]
			toShape = self.subShapes[i]
			transform = (
				fromShape.params[fromPointName][0] - toShape.params[toPointName][0],
				fromShape.params[fromPointName][1] - toShape.params[toPointName][1]
			)
			toShape.transform(distance=transform)
			toShape.applyTransforms()
		chainStartPointName = pointNames[self.connections[0][0]]
		chainEndPointName = pointNames[self.connections[-1][1]]
		self.params['startPoint'] = self.subShapes[0].params[chainStartPointName]
		self.params['endPoint'] = self.subShapes[-1].params[chainEndPointName]

		