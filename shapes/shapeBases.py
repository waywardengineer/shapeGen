from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *

minLineSize = 0.1

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
			if part not in ['(', ')', '+', '-', '*', '/', ',', 'avgPoints', 'distanceBetween', 'addVectors', '[', ']', 'subtractVectors'] and not isNumeric(part):
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
		return self.resolved
		
	def __getattr__(self, item):
		if item not in ['resolved', 'dir', 'parent'] and item not in self.dir:
			if item in self.keys():
				return self[item].value
			else:
				return False
	def __setattr__(self, item, value):
		if item not in ['resolved', 'dir', 'parent'] and item not in self.dir:
			if item in ['id', 'type', 'traceClass']:
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
	def getCopy(self):
		return Transforms([(Param(self[i][0].value), Param(self[i][1].value)) for i in range(len(self))])
	def printValues(self):
		values = [(t[0].value, t[1].value) for t in self]
		print values

class Shape(object):
	defaultParams = {}
	def __init__(self, params):
		params = dict(self.defaultParams, **params)
		self.p = Params(self, params)
		self.transforms = Transforms()
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
			self.p.printValues()
			raise Exception("error finding param")
		self.applyTransforms()

	def addToDrawing(self, drawing, layer='0'):
		if not self.p.excludeSubShapes:
			for subShape in self.subShapes:
				subShape.addToDrawing(drawing, layer)

	def transform(self, angle = 0, distance = (0, 0)):
		self.transforms.append((Param(angle), Param(distance)))

	def applyTransforms(self):
		self.calculate()
		while len(self.transforms) > 0:
			if self.transforms[0][0].resolve(self) and self.transforms[0][1].resolve(self):
				transform = self.transforms.pop(0)
				for subShape in self.subShapes:
					subShape.transforms.append(transform)
					subShape.applyTransforms()
				angle = transform[0].value
				distance = transform[1].value
				for key in ['startPoint', 'endPoint', 'centerPoint']:
					if key in self.p.keys():
						self.updateParam(key, transformPoint(self.p[key].value, angle, distance))
				for key in ['startAngle', 'endAngle', 'rotationAngle']:
					if key in self.p.keys():
						self.updateParam(key, self.p[key].value + angle)
			else:
				self.p.printValues()
				self.transforms.printValues()
				raise Exception("error finding distance transform")
			self.calculate()

	def getCopy(self, depth = 0, idChain = []):
		newCopy = copy(self)
		idChain = copy(idChain)
		if self.p.id:
			idChain.append(self.p.id)
			depth += 1
		newCopy.p = self.p.getCopy(newCopy)
		newCopy.transforms = self.transforms.getCopy()
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
