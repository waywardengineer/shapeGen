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
		p = self.p #this cell params
		bp = baseShape.p #base tree params 
		p.endPoints = [False for j in range(len(bp.angles))]
		p.subCellIds = [False for j in range(len(bp.angles))]
		for angleIndex in range(len(bp.angles)):
			branchIndex = bp.angleOrder[angleIndex] #relates to where things physically are on the tree
			newBranchAngle = p.angle + baseShape.getBranchAngle(self, angleIndex)
			if newBranchAngle is not None: #getBranchAngle should return none when it wants to randomly skip a branch
				endPoint = addVectors(transformPoint((p.length, 0), newBranchAngle), p.startPoint)
				crossesExisting = False
				for cell in [treeData['cells'][k] for k in treeData['cells']]:
					existingStartPoint = cell.startPoint
					for existingEndPoint in cell.endPoints:
						if existingEndPoint:
							existingLine = (existingStartPoint, existingEndPoint)
							if linesCross(existingLine, (p.startPoint, endPoint), 0.0001, baseShape.getClearanceWidth(cell)):
								crossesExisting = True
								break
					if crossesExisting:
						break
				if crossesExisting:
					continue
				if not p.cellId in treeData['cells']:
					treeData['cells'][p.cellId] = p
					if p.superCellId:
						treeData['cells'][p.superCellId[0]].subCellIds[p.superCellId[1]] = p.cellId
				p.endPoints[branchIndex] = endPoint
				if p.depth < bp.maxDepth and p.length > bp.minLength and p.featureSize > bp.minFeatureSize: 
					directionalityIncrement = float(len(bp.angles) - 1) / 2 - float(branchIndex) #linearly increases as things get more offcenter
					newParamVals = {
						'length' : p.length * getParam(angleIndex, bp.lengthFactor),
						'featureSize' : p.featureSize * getParam(angleIndex, bp.featureSizeFactor),
						'angle' : baseShape.getSubCellAngle(p, newBranchAngle, angleIndex),
						'depth' : p.depth + 1,
						'startPoint' : endPoint,
						'directionalitySum' : p.directionalitySum + directionalityIncrement,
						'superCellId' : (self.p.cellId, branchIndex),
						'cellId' : treeData['nextId']
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
		'length' : 8,
		'featureSize' : 1,
		'angle' : 90,
		'depth' : 0,
		'directionalitySum' : 0,
		'cellId' : 0,
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
			isBranchEnd = not reverse and (currentCell.subCellIds[currentBranchIndex] == False)
			isTreeEnd = reverse and currentCellId == 0 and currentBranchIndex == (len(currentCell.endPoints) - 1)
			forkMade = False
			if isTreeEnd:
				points = getTreeEndPoints(
					(currentCell.endPoints[0], currentCell.startPoint, currentCell.endPoints[-1]),
					self.getJointWidth(currentCell),
					solveFromRight
				)
				for point in points:
					intersectPoints.append({
						'type' : 'treeEnd',
						'point' : point,
						'superCellId' : currentCell.superCellId
					})
				completed = True
			elif isBranchEnd:
				points = getBranchEndPoints(
					(currentCell.startPoint, currentCell.endPoints[currentBranchIndex]),
					self.getJointWidth(currentCell),
					solveFromRight
				)
				for point in points:
					intersectPoints.append({
						'type' : 'branchEnd',
						'point' : point,
						'superCellId' : currentCell.superCellId
					})
				reverse = True
			if not completed:
				if currentCell.endPoints[currentBranchIndex]:
					if reverse:
						points = [
							currentCell.endPoints[currentBranchIndex],
							currentCell.startPoint
						]
						if (len(currentCell.endPoints) - 1) > currentBranchIndex: #maybe fork
							nextBranchIndex = currentBranchIndex + 1
							while nextBranchIndex < len(currentCell.endPoints) and not forkMade:
								if currentCell.endPoints[nextBranchIndex]:
									nextCellId = currentCellId
									points.append(currentCell.endPoints[nextBranchIndex])
									reverse = False
									forkMade = True
								else:
									nextBranchIndex += 1
						if not forkMade: #backwards to next cell
							nextCellId, nextBranchIndex = currentCell.superCellId
							points.append(self.treeData['cells'][nextCellId].startPoint)
					else:
						nextCellId = currentCell.subCellIds[currentBranchIndex]
						nextCell = self.treeData['cells'][nextCellId]
						nextBranchIndex = 0
						points = [
							currentCell.startPoint,
							currentCell.endPoints[currentBranchIndex]
						]
						point = False
						while not point:
							point = nextCell.endPoints[nextBranchIndex]
							if not point:
								nextBranchIndex += 1
						points.append(point)
					point = getOffsetIntersect(points, self.getJointWidth(currentCell), solveFromRight)
					if forkMade or reverse:
						type = 'reversedSide'
					else:
						type = 'side'
					pointData = {
						'type' : type,
						'point' : point,
						'superCellId' : currentCell.superCellId
					}
					intersectPoints.append(pointData)
				else:
					nextBranchIndex = currentBranchIndex + 1
					nextCellId = currentCellId
				currentCellId = nextCellId
				currentBranchIndex = nextBranchIndex
		self.treeData['outlinePoints'] = intersectPoints
		self.drawSides()

	def getJointWidth(self, cell):
		return 0.01 + cell.length * 0.02

	def getClearanceWidth(self, cell):
		return self.getJointWidth(cell) * 1.1

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in self.treeData['cells'].keys()]:
			for endPoint in cell.endPoints:
				if endPoint:
					self.addSubShape(Line({'startPoint' : cell.startPoint, 'endPoint' : endPoint}))

	def getSubCellAngle(self, p, branchAngle, branchIndex):
		bp = self.p
		directionalityAngleAdjustment = pow(abs(p.directionalitySum), bp.directionalityExponent)\
			* bp.directionalityFactor
		if p.directionalitySum < 0:
			directionalityAngleAdjustment =- directionalityAngleAdjustment
		return branchAngle + directionalityAngleAdjustment

	def getBranchAngle(self, cellId, branchIndex):
		return self.p.angles[branchIndex]

class HoneycombSpiral(BranchingShape):
	_outlines = True
	_middlelines = False
	defaultParams = {
		'maxDepth' : 12,
		'angles' : [-50, 70],
		'featureSizeFactor' : [0.75, 0.75],
		'lengthFactor' : [1.2, 0.4],
		'minLength' : 0.1,
		'minFeatureSize' : 0,
		'directionalityExponent' : 0.8,
		'directionalityFactor' : 1,
		'skipPercentage' : 0,
	}

class newThingey(BranchingShape):
	_outlines = True
	_middlelines = True
	defaultParams = {
		'maxDepth' : 6,
		'angles' : [50, 0],
		'featureSizeFactor' : [1.15, 0.5],
		'lengthFactor' : [1.15, 0.6],
		'minLength' : 0.1,
		'minFeatureSize' : 0,
		'directionalityExponent' : 0.8,
		'directionalityFactor' : 1,
		'skipPercentage' : 0,
	}


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
		
		
