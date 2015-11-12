from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *
from shapes import *
from HolesOnArcChain import HolesOnArcChain

from Spiral import Spiral
from random import random
import json

class BranchingShapeCell(Shape):
	def __init__(self, baseShape, *args):
		Shape.__init__(self, *args)
		treeData = baseShape.treeData
		endPoints = []
		p = self.p
		bp = baseShape.p
		for angleIndex in range(len(bp.angles)):
			branchIndex = bp.angleOrder[angleIndex]
			newBranchAngle = p.angle + baseShape.getBranchAngle(self, angleIndex)
			if newBranchAngle is not None:
				length = p.lengthScaling
				endPoint = addVectors(transformPoint((length, 0), newBranchAngle), p.startPoint)
				crossesExisting = False
				for cell in [treeData['cells'][k] for k in treeData['cells'].keys()]:
					existingStartPoint = cell['startPoint']
					for existingEndPoint in cell['endPoints']:
						if existingEndPoint:
							existingLine = (existingStartPoint, existingEndPoint)
							if linesCross(existingLine, (p.startPoint, endPoint), 0.0001):
								crossesExisting = True
								continue
				if (not crossesExisting):
					if not p.idNum in treeData['cells'].keys():
						treeData['cells'][p.idNum] = {
							'shapeObj' : self,
							'endPoints' : [False for j in range(len(bp.angles))],
							'subCellIds' : [False for j in range(len(bp.angles))],
							'startPoint' : p.startPoint,
							'superCellId' : p.superCellId
						}
						if p.superCellId:
							treeData['cells'][p.superCellId[0]]['subCellIds'][p.superCellId[1]] = p.idNum
					treeData['cells'][p.idNum]['endPoints'][branchIndex] = endPoint
					if p.depth < bp.maxDepth and p.lengthScaling > bp.minLengthScaling and p.featureScaling > bp.minFeatureScaling: 
						directionalityIncrement = float(len(bp.angles) - 1) / 2 - float(angleIndex)
						newParamVals = {
							'lengthScaling' : p.lengthScaling * getParam(angleIndex, bp.lengthScalingFactor),
							'featureScaling' : p.featureScaling * getParam(angleIndex, bp.featureScalingFactor),
							'angle' : baseShape.getSubCellAngle(self, angleIndex, newBranchAngle),
							'depth' : p.depth + 1,
							'startPoint' : endPoint,
							'directionalitySum' : p.directionalitySum + directionalityIncrement,
							'superCellId' : (self.p.idNum, branchIndex),
							'idNum' : treeData['nextId']
						}
						treeData['nextId'] += 1
						self.addSubShape(BranchingShapeCell(baseShape, newParamVals))

def getParam(index, param):
	if isinstance(param, list):
		return param[index % len(param)]
	else:
		return param

class BranchingShape(Shape):
	defaultCellParams = {
		'startPoint' : (0, 0),
		'lengthScaling' : 8,
		'featureScaling' : 1,
		'angle' : 90,
		'depth' : 0,
		'directionalitySum' : 0,
		'idNum' : 0,
		'superCellId' : False,
	}
	_outlines = True
	_middlelines = True
	def __init__(self, *args):
		Shape.__init__(self, *args)
		self.treeData = {
			'cells' : {},
			'nextId' : 1
		}
		if self.p.angles:
			self.p.angleOrder = getIndexOrder(self.p.angles)
		self.addSubShape(BranchingShapeCell(self, self.defaultCellParams))
		if self._outlines:
			self.calculateOutlinePoints()
			self.drawSides()
		if self._middlelines:
			self.drawMiddleShapes()

	def calculateOutlinePoints(self):
		currentCellId = 0
		nextCellId = 0
		currentBranchIndex = 0
		nextBranchIndex = 0
		completed = False
		reverse = False
		solveFromRight = True
		intersectPoints = []
		while not completed:
			currentCell = self.treeData['cells'][currentCellId]
			isBranchEnd = not reverse and (currentCell['subCellIds'][currentBranchIndex] == False)
			isTreeEnd = reverse and currentCellId == 0 and currentBranchIndex == (len(currentCell['endPoints']) - 1)
			forkMade = False
			if isTreeEnd:
				points = getTreeEndPoints(
					(currentCell['endPoints'][0], currentCell['startPoint'], currentCell['endPoints'][-1]),
					self.getWidth(currentCellId),
					solveFromRight
				)
				for point in points:
					intersectPoints.append({
						'type' : 'treeEnd',
						'point' : point,
						'superCellId' : currentCell['superCellId']
					})
				completed = True
			elif isBranchEnd:
				points = getBranchEndPoints(
					(currentCell['startPoint'], currentCell['endPoints'][currentBranchIndex]),
					self.getWidth(currentCellId),
					solveFromRight
				)
				for point in points:
					intersectPoints.append({
						'type' : 'branchEnd',
						'point' : point,
						'superCellId' : currentCell['superCellId']
					})
				reverse = True
			if not completed:
				if currentCell['endPoints'][currentBranchIndex]:
					if reverse:
						points = [
							currentCell['endPoints'][currentBranchIndex],
							currentCell['startPoint']
						]
						if (len(currentCell['endPoints']) - 1) > currentBranchIndex: #maybe fork
							nextBranchIndex = currentBranchIndex + 1
							while nextBranchIndex < len(currentCell['endPoints']) and not forkMade:
								if currentCell['endPoints'][nextBranchIndex]:
									nextCellId = currentCellId
									points.append(currentCell['endPoints'][nextBranchIndex])
									reverse = False
									forkMade = True
								else:
									nextBranchIndex += 1
						if not forkMade: #backwards to next cell
							nextCellId, nextBranchIndex = currentCell['superCellId']
							points.append(self.treeData['cells'][nextCellId]['startPoint'])
					else:
						nextCellId = currentCell['subCellIds'][currentBranchIndex]
						nextCell = self.treeData['cells'][nextCellId]
						nextBranchIndex = 0
						points = [
							currentCell['startPoint'],
							currentCell['endPoints'][currentBranchIndex]
						]
						point = False
						while not point:
							point = nextCell['endPoints'][nextBranchIndex]
							if not point:
								nextBranchIndex += 1
						points.append(point)
					point = getOffsetIntersect(points, self.getWidth(currentCellId), solveFromRight)
					if forkMade or reverse:
						type = 'reversedSide'
					else:
						type = 'side'
					pointData = {
						'type' : type,
						'point' : point,
						'superCellId' : currentCell['superCellId']
					}
					intersectPoints.append(pointData)
				else:
					nextBranchIndex = currentBranchIndex + 1
					nextCellId = currentCellId
				currentCellId = nextCellId
				currentBranchIndex = nextBranchIndex
		self.treeData['outlinePoints'] = intersectPoints
		self.drawSides()

	def getWidth(self, cellId):
		return self.treeData['cells'][cellId]['shapeObj'].p.lengthScaling * 0.05

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in self.treeData['cells'].keys()]:
			for endPoint in cell['endPoints']:
				if endPoint:
					self.addSubShape(Line({'startPoint' : cell['startPoint'], 'endPoint' : endPoint}))

	def getSubCellAngle(self, cellObj, branchIndex, newBranchAngle):
		directionalityAngleAdjustment = pow(abs(cellObj.p.directionalitySum), self.p.directionalityAngleAdjustmentExponent)\
			* self.p.directionalityAngleAdjustmentFactor
		if cellObj.p.directionalitySum < 0:
			directionalityAngleAdjustment =- directionalityAngleAdjustment
		return newBranchAngle + directionalityAngleAdjustment

	def getBranchAngle(self, cellObj, branchIndex):
		return self.p.angles[branchIndex]

class HoneycombSpiral(BranchingShape):
	_outlines = True
	_middlelines = True
	defaultParams = {
		'maxDepth' : 10,
		'angles' : [-50, 70],
		'featureScalingFactor' : [0.75, 0.75],
		'lengthScalingFactor' : [1.15, 0.6],
		'minLengthScaling' : 0.1,
		'minFeatureScaling' : 0,
		'directionalityAngleAdjustmentExponent' : 0.8,
		'directionalityAngleAdjustmentFactor' : 1,
		'skipPercentage' : 0,
	}
	def getWidth(self, cellId):
		return 0.015 + self.treeData['cells'][cellId]['shapeObj'].p.lengthScaling * 0.01

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))


class newThingey(BranchingShape):
	_outlines = True
	_middlelines = True
	defaultParams = {
		'maxDepth' : 6,
		'angles' : [50, 0],
		'featureScalingFactor' : [1.15, 0.5],
		'lengthScalingFactor' : [1.15, 0.6],
		'minLengthScaling' : 0.1,
		'minFeatureScaling' : 0,
		'directionalityAngleAdjustmentExponent' : 0.8,
		'directionalityAngleAdjustmentFactor' : 1,
		'skipPercentage' : 0,
	}
	def getWidth(self, cellId):
		return 0.1 + self.treeData['cells'][cellId]['shapeObj'].p.lengthScaling * 0.001

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))
	
	def getBranchAngle(self, cellObj, branchIndex):
		angle = self.p.angles[branchIndex]
		# if cellObj.p.depth % 2:
			# angle = -angle
		return angle

def randomAngle(center, range):
	return center - (range / 2) + random() * range

def getIndexOrder(l):
	valuesWithIndexes = [(v, i) for i, v in enumerate(l)]
	result = []
	while len(valuesWithIndexes) > 0:
		pair = min(valuesWithIndexes)
		result.append(pair[1])
		valuesWithIndexes.remove(pair)
	return result
		
		
