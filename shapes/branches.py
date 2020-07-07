from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from .shapeUtils import *
from .shapeBases import *
from .shapes import *
from .HolesOnArcChain import HolesOnArcChain

from .Spiral import Spiral
from random import random
import json


class BranchingShapeCell(Shape):
	def __init__(self, baseShape, *args):
		Shape.__init__(self, *args)
		treeData = baseShape.treeData
		p = self.p  # this cell params
		bp = baseShape.p  # base tree params
		p.endPoints = [False for j in range(len(bp.angles))]
		p.subCellIds = [False for j in range(len(bp.angles))]
		for angleIndex in range(len(bp.angles)):
			if random() <= 0.01 * bp.skipPercentage:
				continue
			if angleIndex > 0:
				if bp.minBranchingDepth and bp.minBranchingDepth > p.depth:
					continue
				if bp.branchIntervals and (p.depth + bp.branchIntervalOffsets[angleIndex]) % bp.branchIntervals[angleIndex] > 0:
					continue

			length = p.length * getParam(angleIndex, bp.lengthFactor)
			branchIndex = bp.angleOrder[angleIndex]  # relates to where things physically are on the tree
			branchAngle = baseShape.getBranchAngle(self, angleIndex)
			newBranchAngle = p.angle + branchAngle
			endPoint = addVectors(transformPoint((length, 0), newBranchAngle), p.startPoint)
			crossesExisting = False
			for cell in [treeData['cells'][k] for k in treeData['cells']]:
				existingStartPoint = cell.startPoint
				for existingEndPoint in cell.endPoints:
					if existingEndPoint:
						existingLine = (existingStartPoint, existingEndPoint)
						if linesCross(existingLine, (p.startPoint, endPoint), 0.001,
									  baseShape.getClearanceWidth(cell)):
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
				directionalityIncrement = float(len(bp.angles) - 1) / 2 - float(
					branchIndex)  # linearly increases as things get more offcenter
				newParamVals = {
					'length': length,
					'featureSize': p.featureSize * getParam(angleIndex, bp.featureSizeFactor),
					'angle': baseShape.getSubCellAngle(p, newBranchAngle, angleIndex),
					'depth': p.depth + 1,
					'startPoint': endPoint,
					'directionalitySum': p.directionalitySum + directionalityIncrement,
					'superCellId': (self.p.cellId, branchIndex),
					'cellId': treeData['nextId']
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
		'startPoint': (0, 0),
		'depth': 0,
		'directionalitySum': 0,
		'cellId': 0,
		'superCellId': False,
		'angle': 0,
	}
	_outlines = True
	_middlelines = True

	def __init__(self, *args):
		Shape.__init__(self, *args)
		self.treeData = {
			'cells': {},
			'nextId': 1
		}
		if self.p.angles:
			self.p.angleOrder = getIndexOrder(self.p.angles)
		if self.p.featureSize:
			self.defaultCellParams['featureSize'] = self.p.featureSize
		if self.p.startPoint:
			self.defaultCellParams['startPoint'] = self.p.startPoint
		if self.p.length:
			self.defaultCellParams['length'] = self.p.length
		if self.p.angle:
			self.defaultCellParams['angle'] = self.p.angle
		self.addSubShape(BranchingShapeCell(self, self.defaultCellParams))
		if self._outlines:
			self.calculateOutlinePoints()
			self.drawSides()
		if self._middlelines:
			self.drawMiddleShapes()

	@staticmethod
	def countEndpointsUsed(endPointsList):
		count = 0
		for endPoint in endPointsList:
			if endPoint:
				count += 1
		return count

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
			isTreeEnd = reverse and currentCellId == 0 and currentBranchIndex >= (
						self.countEndpointsUsed(currentCell.endPoints) - 1)
			forkMade = False
			if isTreeEnd:
				endPoint = False
				index = -1
				while not endPoint:
					endPoint = currentCell.endPoints[index]
					if not endPoint:
						index -= 1
				points = getTreeEndPoints(
					(currentCell.endPoints[0], currentCell.startPoint, endPoint),
					self.getJointWidth(currentCell),
					solveFromRight
				)
				for point in points:
					intersectPoints.append({
						'type': 'treeEnd',
						'point': point,
						'cell': currentCell
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
						'type': 'branchEnd',
						'point': point,
						'cell': currentCell
					})
				reverse = True
			if not completed:
				if currentCell.endPoints[currentBranchIndex]:
					if reverse:
						points = [
							currentCell.endPoints[currentBranchIndex],
							currentCell.startPoint
						]
						if (len(currentCell.endPoints) - 1) > currentBranchIndex:  # maybe fork
							nextBranchIndex = currentBranchIndex + 1
							while nextBranchIndex < len(currentCell.endPoints) and not forkMade:
								if currentCell.endPoints[nextBranchIndex]:
									nextCellId = currentCellId
									points.append(currentCell.endPoints[nextBranchIndex])
									reverse = False
									forkMade = True
								else:
									nextBranchIndex += 1
						if not forkMade:  # backwards to next cell
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
						'type': type,
						'point': point,
						'cell': currentCell
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
		return self.getJointWidth(cell) * 2

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			self.addSubShape(Line({'startPoint': thisPoint['point'], 'endPoint': nextPoint['point']}))

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in list(self.treeData['cells'].keys())]:
			for endPoint in cell.endPoints:
				if endPoint:
					self.addSubShape(Line({'startPoint': cell.startPoint, 'endPoint': endPoint}))

	def getSubCellAngle(self, p, branchAngle, branchIndex):
		bp = self.p
		directionalityAngleAdjustment = pow(abs(p.directionalitySum), bp.directionalityExponent) * bp.directionalityFactor
		depthAngleAdjustment = pow(abs(p.depth), bp.depthExponent) * bp.depthFactor
		if p.directionalitySum < 0:
			directionalityAngleAdjustment = - directionalityAngleAdjustment
		return branchAngle + directionalityAngleAdjustment + depthAngleAdjustment

	def getBranchAngle(self, cellId, angleIndex):
		return self.p.angles[angleIndex]


class CirclesAndLines(BranchingShape):
	_outlines = False
	_middlelines = True

	def getClearanceWidth(self, cell):
		return self.p.featureSize

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in list(self.treeData['cells'].keys())]:
			self.addSubShape(Circle({'centerPoint': cell.startPoint, 'radius': cell.featureSize}))
			for endPoint in cell.endPoints:
				if endPoint:
					self.addSubShape(Line({'startPoint': cell.startPoint, 'endPoint': endPoint}))


class Circles(BranchingShape):
	_outlines = False
	_middlelines = True

	def getClearanceWidth(self, cell):
		return self.p.featureSize

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in list(self.treeData['cells'].keys())]:
			self.addSubShape(Circle({'centerPoint': cell.startPoint, 'radius': cell.featureSize}))


class Lines(BranchingShape):
	_outlines = False
	_middlelines = True

	def getClearanceWidth(self, cell):
		return self.getJointWidth(cell) * 0.9

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in list(self.treeData['cells'].keys())]:
			for endPoint in cell.endPoints:
				if endPoint:
					self.addSubShape(Line({'startPoint': cell.startPoint, 'endPoint': endPoint}))


class HoneycombSpiral2(BranchingShape):
	_outlines = False
	_middlelines = True
	defaultParams = {
		'maxDepth': 6,
		'angles': [-50, 70],
		'featureSizeFactor': [1.15, 0.6],
		'lengthFactor': [1.15, 0.6],
		'minLength': 0.1,
		'minFeatureSize': 0,
		'directionalityExponent': 0.8,
		'directionalityFactor': 1,
	}

	def getClearanceWidth(self, cell):
		return self.getJointWidth(cell) * 0.9

	def drawMiddleShapes(self):
		for cell in [self.treeData['cells'][k] for k in list(self.treeData['cells'].keys())]:
			self.addSubShape(Circle({'centerPoint': cell.startPoint, 'radius': cell.featureSize}))


class newThingey(BranchingShape):
	defaultCellParams = {
		'startPoint': (0, 0),
		'length': 8,
		'featureSize': 12,
		'angle': 90,
		'depth': 0,
		'directionalitySum': 0,
		'cellId': 0,
		'superCellId': False,
	}
	_outlines = True
	_middlelines = False
	defaultParams = {
		'maxDepth': 6,
		'angles': [20, -30, 0],
		'featureSizeFactor': [1.15, 0.6, 0.5],
		'lengthFactor': [1.15, 0.6, 0.5],
		'minLength': 0.1,
		'minFeatureSize': 0,
		'directionalityExponent': 0.7,
		'directionalityFactor': 1,
		'skipPercentage': 0,
	}

	def getBranchAngle(self, cellId, angleIndex):
		if random() * 100 < 10:
			return None
		return self.p.angles[angleIndex]

	def drawSides(self):
		for i in range(len(self.treeData['outlinePoints'])):
			thisPoint = self.treeData['outlinePoints'][i]
			nextPoint = self.treeData['outlinePoints'][(i + 1) % len(self.treeData['outlinePoints'])]
			if nextPoint['type'] == 'side':
				self.addSubShape(Arc({'startPoint': thisPoint['point'], 'endPoint': nextPoint['point'],
									  'radius': thisPoint['cell'].featureSize}))
			elif nextPoint['type'] == 'reversedSide':
				self.addSubShape(Arc({'startPoint': nextPoint['point'], 'endPoint': thisPoint['point'],
									  'radius': thisPoint['cell'].featureSize}))
			else:
				self.addSubShape(Line({'startPoint': thisPoint['point'], 'endPoint': nextPoint['point']}))


def randomAngle(center, range):
	return center - (range / 2) + random() * range


def getIndexOrder(l):
	valuesWithIndexes = [(v, i) for i, v in enumerate(l)]
	result = [None for i in range(len(l))]
	for i in range(len(l)):
		pair = min(valuesWithIndexes)
		result[pair[1]] = i
		valuesWithIndexes.remove(pair)
	return result
