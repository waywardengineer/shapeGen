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

class BranchingShapeElement(Shape):
	defaultParams = {
		'depth' : 0,
		'directionalitySum' : 0,
		'skipPercentage' : 0,
		'idNum' : 0,
		'parentCellId' : False,
		'startPoint' : (0, 0),
	}
	def __init__(self, treeData, *args):
		Shape.__init__(self, *args)
		paramVals = {k : self.p[k].value for k in self.p.keys()}
		endPoints = []
		p = self.p
		numEndPoints = 0
		for i in range(len(p.angles)):
			length = p.lengthScaling * getParam(i, p.lengthScalingFactor)
			endPoint = addVectors(transformPoint((length, 0), p.angle + p.angles[i]), p.startPoint)
			crossesExisting = False
			for cell in [treeData['cells'][k] for k in treeData['cells'].keys()]:
				existingStartPoint = cell['startPoint']
				for existingEndPoint in cell['endPoints']:
					existingLine = (existingStartPoint, existingEndPoint)
					if linesCross(existingLine, (p.startPoint, endPoint), 0.0001):
						crossesExisting = True
						continue
			if (not crossesExisting) and 100 * random() > p.skipPercentage:
				if not p.idNum in treeData['cells'].keys():
					treeData['cells'][p.idNum] = {
						'shapeObj' : self,
						'endPoints' : [],
						'endPointChildIds' : [],
						'startPoint' : p.startPoint,
						'parentBranch' : p.parentCellId
					}
					if p.parentCellId:
						treeData['cells'][p.parentCellId[0]]['endPointChildIds'][p.parentCellId[1]] = p.idNum
				treeData['cells'][p.idNum]['endPoints'].append(endPoint)
				treeData['cells'][p.idNum]['endPointChildIds'].append(False)
				if p.depth < p.maxDepth and p.lengthScaling > p.minLengthScaling and p.featureScaling > p.minFeatureScaling: 
					directionalityIncrement = float(len(p.angles) - 1) / 2 - float(i)
					directionalityAngleAdjustment = pow(abs(p.directionalitySum), p.directionalityAngleAdjustmentExponent) * p.directionalityAngleAdjustmentFactor
					if p.directionalitySum < 0:
						directionalityAngleAdjustment =- directionalityAngleAdjustment
					newParamVals = copy(paramVals)
					newParamVals['lengthScaling'] *= getParam(i, p.lengthScalingFactor[i])
					newParamVals['featureScaling'] *= getParam(i, p.featureScalingFactor[i])
					newParamVals['angle'] = p.angle + directionalityAngleAdjustment + p.angles[i]
					newParamVals['depth'] = p.depth + 1
					newParamVals['startPoint'] = endPoint
					newParamVals['directionalitySum'] += directionalityIncrement
					newParamVals['parentCellId'] = (self.p.idNum, numEndPoints)
					newParamVals['idNum'] = treeData['nextId']
					treeData['nextId'] += 1
					self.addSubShape(BranchingShapeElement(treeData, newParamVals))
				numEndPoints += 1

def getParam(index, param):
	if isinstance(param, list):
		return param[index % len(param)]
	else:
		return param

class BranchingShape(Shape):
	_outlines = True
	_middlelines = True
	def __init__(self, *args):
		Shape.__init__(self, *args)
		self.treeData = {
			'cells' : {},
			'nextId' : 1
		}
		self.addSubShape(BranchingShapeElement(self.treeData, self.p.dumpValues()))
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
		solveFromRight = self.p.angles[0] < self.p.angles[-1]
		intersectPoints = []
		while not completed:
			currentCell = self.treeData['cells'][currentCellId]
			isBranchEnd = not reverse and (currentCell['endPointChildIds'][currentBranchIndex] == False)
			isTreeEnd = reverse and currentCellId == 0 and currentBranchIndex == (len(currentCell['endPoints']) - 1)
			isFork = False
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
						'parentBranch' : currentCell['parentBranch']
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
						'parentBranch' : currentCell['parentBranch']
					})
				reverse = True
			if not completed:
				if reverse:
					points = [
						currentCell['endPoints'][currentBranchIndex],
						currentCell['startPoint']
					]
					if (len(currentCell['endPoints']) - 1) > currentBranchIndex: #fork
						nextBranchIndex = currentBranchIndex + 1
						nextCellId = currentCellId
						points.append(currentCell['endPoints'][nextBranchIndex])
						reverse = False
						isFork = True
					else: #backwards to next cell
						(nextCellId, nextBranchIndex) = currentCell['parentBranch']
						points.append(self.treeData['cells'][nextCellId]['startPoint'])
				else:
					nextCellId = currentCell['endPointChildIds'][currentBranchIndex]
					nextBranchIndex = 0
					points = [
						currentCell['startPoint'],
						currentCell['endPoints'][currentBranchIndex],
						self.treeData['cells'][nextCellId]['endPoints'][nextBranchIndex]
					]
				point = getOffsetIntersect(points, self.getWidth(currentCellId), solveFromRight)
				if isFork or reverse:
					type = 'reversedSide'
				else:
					type = 'side'
				pointData = {
					'type' : type,
					'point' : point,
					'parentBranch' : currentCell['parentBranch']
				}
				intersectPoints.append(pointData)
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
				self.addSubShape(Line({'startPoint' : cell['startPoint'], 'endPoint' : endPoint}))


class HoneycombSpiral(BranchingShape):
	_outlines = True
	_middlelines = False
	defaultParams = {
		'startPoint' : (0, 0),
		'lengthScaling' : 8,
		'featureScaling' : 1,
		'angle' : 90,
		'maxDepth' : 8,
		'angles' : [-50, 70],
		'featureScalingFactor' : [1.15, 0.5],
		'lengthScalingFactor' : [1.15, 0.5],
		'minLengthScaling' : 0.1,
		'minFeatureScaling' : 0,
		'directionalityAngleAdjustmentExponent' : 0.8,
		'directionalityAngleAdjustmentFactor' : 1,
		'skipPercentage' : 0
	}
	def getWidth(self, cellId):
		return 0.01 + self.treeData['cells'][cellId]['shapeObj'].p.lengthScaling * 0.001

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))

class newThingey(BranchingShape):
	_outlines = True
	_middlelines = True
	defaultParams = {
		'startPoint' : (0, 0),
		'lengthScaling' : 8,
		'featureScaling' : 1,
		'angle' : 90,
		'maxDepth' : 8,
		'angles' : [-50, 70],
		'featureScalingFactor' : [1.15, 0.5],
		'lengthScalingFactor' : [1.15, 0.5],
		'minLengthScaling' : 0.1,
		'minFeatureScaling' : 0,
		'directionalityAngleAdjustmentExponent' : 0.8,
		'directionalityAngleAdjustmentFactor' : 1,
		'skipPercentage' : 0
	}
	def getWidth(self, cellId):
		return 0.1 + self.treeData['cells'][cellId]['shapeObj'].p.lengthScaling * 0.001

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint' : thisPoint['point'], 'endPoint' : nextPoint['point']}))
