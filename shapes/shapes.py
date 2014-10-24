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

def avgPoints (*points):
	result = [sum([points[i][j] for i in range(len(points))]) / len(points) for j in range(len(points[0]))] 
	return tuple(result)
	
	
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


class Param(object):
	def __init__(self, value, type = float):
		self.value = value
		self.resolved = isinstance(value, type)
		self.type = type
	def resolve(self, parent):
		if not self.resolved:
			success = True
			if isinstance(self.value, tuple):
				newValues = []
				for value in self.value:
					if isinstance(value, basestring):
						newSuccess, value = self.getParamVal(value, parent)
						success = newSuccess and success
					newValues.append(value)
				if success:
					self.value = tuple(newValues)
			else:
				if isinstance(self.value, basestring):
					success, value = self.getParamVal(self.value, parent)
					if success:
						self.value = value
			self.resolved = success
		return self.resolved

	def getParamVal(self, paramString, parent):
		parts = paramString.split(' ')
		error = False
		value = 0
		for i in range(len(parts)):
			part = parts[i]
			if part not in ['(', ')', '+', '-', '*', '/', ',', 'avgPoints', 'distanceBetween'] and not isNumeric(part):
				identifier = part.split('.')
				result = parent.doParamSearch(identifier)
				if result is None or isinstance(result, basestring):
					error = True
				else:
					parts[i] = str(result)
		if not error:
			paramString = ''.join(parts)
			value = eval(paramString)
		return (not error, value)

class Params(dict):
	def __init__(self, parent, params):
		dict.__init__(self)
		self.resolved = False
		self.dir = dir(self)
		self.parent = parent
		for key in params.keys():
			self.__setattr__(key, params[key])
	def resolve(self):
		pendingKeys = self.keys()
		numPendingKeys = len(pendingKeys)
		finished = False
		while not finished:
			newPendingKeys = []
			for key in pendingKeys:
				if not self[key].resolve(self.parent):
					newPendingKeys.append(key)
			newNumPendingKeys = len(newPendingKeys)
			finished = newNumPendingKeys == 0 or newNumPendingKeys == numPendingKeys
			pendingKeys = newPendingKeys
			numPendingKeys = newNumPendingKeys
		self.resolved = numPendingKeys == 0
	def __getattr__(self, item):
		if item not in ['resolved', 'dir', 'parent'] and item not in self.dir:
			if item in self.keys():
				return self[item].value
			else:
				return False
	def __setattr__(self, item, value):
		if item not in ['resolved', 'dir', 'parent'] and item not in self.dir:
			if item in ['id', 'type']:
				type = basestring
			elif item in ['reverse']:
				type = bool
			else:
				type = float
			self[item] = Param(value, type)
		else:
			dict.__setattr__(self, item, value)
	def getCopy(self, newParent):
		return Params(newParent, {k: self[k].value for k in self.keys()})
	def printValues(self):
		values = {k : self[k].value for k in self.keys()}
		print values
	

class Transforms(list):
	def __init__(self, parent, *args, **kwargs):
		list.__init__(self, *args, **kwargs)
		self.resolved = False
		self.parent = parent
	def resolve(self):
		foundUnresolvable = False
		i = 0
		if len(self) > 0:
			while not foundUnresolvable and i < len(self):
				if self[i][0] and not self[i][0].resolve(self.parent):
					foundUnresolvable = True
				if self[i][1] and not self[i][1].resolve(self.parent):
					foundUnresolvable = True
				i += 1
		self.resolved = not foundUnresolvable
	def getCopy(self, newParent):
		return Transforms(newParent, [(Param(self[i][0].value), Param(self[i][1].value)) for i in range(len(self))])
	def printValues(self):
		values = [(t[0].value, t[1].value) for t in self]
		print values
class Shape(object):
	def __init__(self, params):
		self.p = Params(self, params)
		self.transforms = Transforms(self)
		self.subShapes = []
		self.parent = False
		self.timesCopied = 0
		self.p.type = self.__class__.__name__
		self.pChecked = False
		self.error = False
		
	def build(self, topShape):
		self.topShape = topShape
		for subShape in self.subShapes:
			subShape.build(topShape)
		rejectedKeys = []
		self.p.resolve()
		if not self.p.resolved:
			raise Exception("error finding param")
		self.transforms.resolve()
		self.applyResolvedTransforms()
		if not self.transforms.resolved:
			self.transforms.resolve()
			if not self.transforms.resolved:
				self.transforms.printValues()
				raise Exception("error finding distance transform")
			self.applyResolvedTransforms()

	def addToDrawing(self, drawing, layer='0'):
		if not self.p.dontRenderSubShapes:
			for subShape in self.subShapes:
				subShape.addToDrawing(drawing, layer)

	def transform(self, angle = 0, distance = (0, 0)):
		self.transforms.append((Param(angle), Param(distance)))

	def applyResolvedTransforms(self):
		foundUnresolved = False
		while len(self.transforms) > 0 and not foundUnresolved:
			if self.transforms[0][0].resolved and self.transforms[0][1].resolved:
				transform = self.transforms.pop(0)
				for subShape in self.subShapes:
					subShape.transforms.append(transform)
					subShape.applyResolvedTransforms()
				angle = transform[0].value
				distance = transform[1].value
				for key in ['startPoint', 'endPoint', 'centerPoint']:
					if key in self.p.keys():
						self.updateParam(key, transformPoint(self.p[key].value, angle, distance))
				for key in ['startAngle', 'endAngle', 'rotationAngle']:
					if key in self.p.keys():
						self.updateParam(key, self.p[key].value + angle)
			else:
				foundUnresolved = True
		self.calculate()

	def getCopy(self, depth = 0, idChain = []):
		newCopy = copy(self)
		idChain = copy(idChain)
		if self.p.id:
			idChain.append(self.p.id)
			depth += 1
		newCopy.p = self.p.getCopy(newCopy)
		newCopy.transforms = self.transforms.getCopy(newCopy)
		newCopy.subShapes = [s.getCopy(depth, idChain) for s in self.subShapes]
		for shape in newCopy.subShapes:
			shape.setParent(newCopy)
		if self.p.changeableParams:
			for paramKey in self.p.changeableParams:
				paramChain = idChain + [paramKey]
				newCopy.updateParam(paramKey, '.'.join(paramChain))
		if self.p.id and depth == 1:
			self.timesCopied += 1
			newCopy.p.id = newCopy.p.id + str(self.timesCopied)
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
				changeableParamsData = {k : self.p[k] for k in self.p.changeableParams}
			else:
				changeableParamsData = {}
			data.append({'id' : self.p.id, 'changeableParams' : changeableParamsData, 'object' : self})
		return data

	def updateParam(self, param, value):
		self.p.__setattr__(param, value)


	def calculate(self):
		pass

	def clearParamCheckState(self):
		self.pChecked = False
		for shape in self.subShapes:
			shape.clearParamCheckState()
	def doParamSearch(self, identifier):
		self.topShape.clearParamCheckState()
		identifier = deepcopy(identifier)
		result = self.doParamSubsearch(identifier, False, 0)
		return result[0]

	def doParamSubsearch(self, identifier, downOnly, distance):
		if self.pChecked:
			return (None, distance)
		self.pChecked = True
		if len(identifier) == 1:
			if identifier[0] in self.p.keys():
				return (self.p[identifier[0]].value, distance)
			else:
				return (None, distance)
		if len(identifier) == 2:
			if identifier[0] == self.p.id:
				if identifier[1] in self.p.keys():
					return (self.p[identifier[1]].value, distance)
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

class Circle(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer)
		circle = dxf.circle(self.p.radius, self.p.centerPoint, layer=layer)
		drawing.add(circle)


class Arc(Shape):
	def calculate(self, *args): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
		if listContains(['startPoint', 'startAngle', 'endPoint'], self.p.keys()):
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
				self.p.startAngle = self.p.startAngle + 180
			self.p.radius = radius
			self.p.centerPoint = centerPoint
			self.p.endAngle = degrees(endAngleRads)
		elif listContains(['startPoint', 'startAngle', 'radius', 'endAngle'], self.p.keys()):
			startPoint = self.p.startPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
			self.p.centerPoint = centerPoint
			self.p.endPoint = endPoint
		elif listContains(['endPoint', 'startAngle', 'radius', 'endAngle'], self.p.keys()):
			endPoint = self.p.endPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (endPoint[0] - radius * cos(endAngleRads), endPoint[1] - radius * sin(endAngleRads))
			startPoint = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.p.centerPoint = centerPoint
			self.p.startPoint = startPoint
		elif listContains(['centerPoint', 'radius', 'startAngle', 'endAngle'], self.p.keys()):
			centerPoint = self.p.centerPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			self.p.startPoint = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.p.endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
		else:
			print self.p
			raise Exception('No valid combination of arc data')
		if self.p.reverse:
			angleSpan = self.p.startAngle - self.p.endAngle
		else:
			angleSpan = self.p.endAngle - self.p.startAngle
		angleSpan = (angleSpan + 720) % 360
		self.p.angleSpan = angleSpan
		self.p.arcLength = self.p.radius * 2 * pi * angleSpan / 360.


	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer) 
		if not self.error:
			if self.p.reverse:
				arc = dxf.arc(self.p.radius, self.p.centerPoint, self.p.endAngle, self.p.startAngle, layer = '0')
			else:
				arc = dxf.arc(self.p.radius, self.p.centerPoint, self.p.startAngle, self.p.endAngle, layer = '0')
			drawing.add(arc)


class BezCurve(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing) #params: {'points' : [((x, y), angle, (strengthIn, strengthOut))]}
		curve = dxf.bezier(layer = layer)
		points = self.p['points']
		vectors = self.makeVectors(self.p['points'][0])
		curve.start(points[0][0], vectors[1])
		for i in range(1, len(points)):
			strengthIn = points[i][2][0]
			strengthOut = points[i][2][1]
			angle = radians(points[i][1])
			vectors = self.makeVectors(self.p['points'][i])
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
			for point in self.p['points']:
				newPoint = (
					transformPoint(point[0], angle, distance),
					point[1] + angle,
					point[2]
				)
				newPoints.append(newPoint)
			self.p['points'] = newPoints


class Spiral(Shape):
	def getRadius(self, angleFromStart):
		b = 0.0053468
		radius = self.p.scaleFactor * pow(e, b * self.p.growthFactorAdjustment * angleFromStart)
		return radius

	def calculate(self, *args): 
		if self.p.sweepStartAngle:
			angleFromStart = self.p.sweepStartAngle
		else:
			angleFromStart = 0
		self.p.sweepEndAngle = angleFromStart + self.p.sweepAngleSpan
		self.points = []
		self.arcLengthLookup = []
		if self.p.reverse:
			direction = -1
		else:
			direction = 1
		arcLength = 0
		finished = False
		while not finished:
			if angleFromStart > self.p.sweepEndAngle:
				angleFromStart = self.p.sweepEndAngle
			finished = angleFromStart >= self.p.sweepEndAngle
			radius = self.getRadius(angleFromStart)
			if not ('minRadius' in self.p.keys() and radius < self.p.minRadius):
				pointInPolar = (self.p.rotationAngle + direction * angleFromStart, radius)
				point = addVectors(polarToCartesian(pointInPolar), self.p.centerPoint)
				if len(self.points) > 0:
					arcLength += distanceBetween(point, self.points[-1])
					self.arcLengthLookup.append((angleFromStart, arcLength))
				self.points.append(point)
			angleFromStart += minLineSize / (sin(radians(1)) * radius)
		self.p.arcLength = arcLength
		self.p.endPoint = self.points[-1]
		self.p.endAngle = degrees(atan2(self.points[-1][1] - self.points[-2][1], self.points[-1][0] - self.points[-2][0])) + 90
		self.p.startPoint = self.points[0]
		self.p.startAngle = degrees(atan2(self.points[0][1] - self.points[1][1], self.points[0][0] - self.points[1][0])) + 90

	def lookupArcLength(self, angleFromStart):
		result = [i for i, v in enumerate(self.arcLengthLookup) if v[0] < angleFromStart]
		if len(result) == 0:
			return 0
		elif len(result) == len(self.arcLengthLookup):
			return self.p.arcLength
		else:
			return interpolate(angleFromStart, self.arcLengthLookup[result[-1]], self.arcLengthLookup[result[-1] + 1]) 
			
	def addToDrawing(self, drawing, layer='0'):
		for i in range(1, len(self.points)):
			line = dxf.line(self.points[i-1], self.points[i], layer=layer)
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
						angleChangeStr = ' + 180'
					if shape.p.prepend:
						shape.updateParam('endPoint', '.'.join([lastShape.p.id, 'startPoint']))
						shape.updateParam('endAngle', '.'.join([lastShape.p.id, 'startAngle' + angleChangeStr]))
					else:
						shape.updateParam('startPoint', '.'.join([lastShape.p.id, 'endPoint']))
						shape.updateParam('startAngle', '.'.join([lastShape.p.id, 'endAngle' + angleChangeStr]))
			if shape.p.type == 'Arc' and shape.p.angleSpan:
				if shape.p.prepend:
					if shape.p.reverse:
						startAngleStr = 'endAngle + ' + str(shape.p.angleSpan)
					else:
						startAngleStr = 'endAngle - ' + str(shape.p.angleSpan)
					shape.updateParam('startAngle', startAngleStr)
				else:
					if shape.p.reverse:
						endAngleStr = 'startAngle - ' + str(shape.p.angleSpan)
					else:
						endAngleStr = 'startAngle + ' + str(shape.p.angleSpan)
					shape.updateParam('endAngle', endAngleStr)

	def calculate(self):
		newSubShapes =  []
		for shape in self.subShapes:
			if shape.p.prepend:
				newSubShapes = [shape] + newSubShapes
			else:
				newSubShapes.append(shape)
		self.subShapes = newSubShapes
		self.p.startPoint = self.subShapes[0].p.startPoint
		self.p.startAngle = self.subShapes[0].p.startAngle
		self.p.endPoint = self.subShapes[-1].p.endPoint
		self.p.endAngle = self.subShapes[-1].p.endAngle

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
				startAngle = arc.p.rotationAngle
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
			error = 500
			lastError = 1000
			while 5 < error < lastError:
				lastError = error
				newCenterPoint = getCenterPoint(newArcIndex, angle)
				distanceToNextHole = hypot(lastCenterPoint[0] - newCenterPoint[0], lastCenterPoint[1] - newCenterPoint[1])
				error = 100. * (targetDistanceToNextHole - distanceToNextHole) / targetDistanceToNextHole
				angle += 0.25
			return angle
		self.subShapes = [self.subShapes[0]]
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
				skip = False
				if thisRadius < self.p.minRadius:
					skip = True
				# skip = skip or distanceBetween(centerPoint, 
				if skip:
					print 'skipping'
				if not skip:
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
				getattr(fromShape.p, fromPointName)[0] - getattr(toShape.p, toPointName)[0],
				getattr(fromShape.p, fromPointName)[1] - getattr(toShape.p, toPointName)[1]
			)
			toShape.transform(distance=transform)
			toShape.transforms.resolve()
			toShape.applyResolvedTransforms()
		chainStartPointName = pointNames[self.connections[0][0]]
		chainEndPointName = pointNames[self.connections[-1][1]]
		self.p.startPoint = getattr(self.subShapes[0].p, chainStartPointName)
		self.p.endPoint = getattr(self.subShapes[-1].p, chainEndPointName)

		