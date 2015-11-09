from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *
from shapes import *
from HolesOnArcChain import HolesOnArcChain

from Spiral import Spiral
from random import random


class CirclesAtNodes(Shape):
	defaultParams = {
		'baseLength' : 10,
		'branchAngles' : [15, 0, -15],
		'baseRadius' : 0.25,
	}
	def __init__(self, treeData, params):
		Shape.__init__(self, params)
		self.crossesLimit = False
		mainLength = 0.9 * self.p.lengthScaling * self.p.baseLength
		branchLength = 0.1 * self.p.lengthScaling * self.p.baseLength
		branchPoint = addVectors(transformPoint((mainLength, 0), self.p.angle), self.p.startPoint)
		endPoints = []
		for i in range(len(self.p.branchAngles)):
			endPoint = addVectors(transformPoint((branchLength, 0), self.p.angle + self.p.branchAngles[i]), branchPoint)
			endPoints.append(endPoint)
		radius = self.p.baseRadius * self.p.featureScaling
		if radius > self.p.minRadius:
			self.addSubShape(Circle({'radius' : radius, 'centerPoint' : endPoint}))
		self.p.endPoints = endPoints
			
class Lines(Shape):
	defaultParams = {
		'baseLength' : 10,
		'branchAngles' : [60, -60],
	}
	def __init__(self, treeData, params):
		Shape.__init__(self, params)
		def addLine(startPoint, endPoint):
			crossesExisting = False
			for existingLine in treeData['lines']:
				if linesCross(existingLine, (startPoint, endPoint), 0.0001) or linesCross((startPoint, endPoint), existingLine, 0.0001):
					crossesExisting = True
					continue
			if not crossesExisting:
				treeData['lines'].append((startPoint, endPoint))
				self.addSubShape(Line({'startPoint' : startPoint, 'endPoint' : endPoint}))
			return not crossesExisting
		mainLength = 1 * self.p.lengthScaling * self.p.baseLength
		branchLength = 0 * self.p.lengthScaling * self.p.baseLength
		forkingPoint = addVectors(transformPoint((mainLength, 0), self.p.angle), self.p.startPoint)
		endPoints = []
		if not 'lines' in treeData.keys():
			treeData['lines'] = []
		if addLine(self.p.startPoint, forkingPoint):
			for i in range(len(self.p.branchAngles)):
				endPoint = addVectors(transformPoint((branchLength, 0), self.p.angle + self.p.branchAngles[i]), forkingPoint)
				if addLine(forkingPoint, endPoint):
					endPoints.append(endPoint)
		self.crossesLimit = len(endPoints) == 0
		self.p.endPoints = endPoints

class OutlinedCurvingTwo(Shape):
	defaultParams = {
		'baseLength' : 10,
		'baseRadius' : 15,
	}
	def __init__(self, params):
		Shape.__init__(self, params)
		p = self.p
		p.endPoints = [
			addVectors(transformPoint((p.baseLength * p.lengthScaling, 0), p.angle + p.angles[0] * 0.25), p.startPoint),
			addVectors(transformPoint((p.baseLength * p.lengthScaling, 0), p.angle + p.angles[1] * 0.25), p.startPoint),
		]
		startArcL = Arc({
			'startPoint' : p.startPoint,
			'radius' : 0.1 * p.baseRadius * p.featureScaling,
			'startAngle' : p.angle - 80,
			'endAngle' : p.angle - 10,
			'id' : 'startArcL'
		})
		outsideEndArcL = Arc({
			'startPoint' : subtractVectors(p.endPoints[0], transformPoint((p.baseLength * p.lengthScaling * 0.05, 0), angle = p.angle + p.angles[0])),
			'radius' : 0.11 * p.baseRadius * p.featureScaling * p.featureScalingFactor[0],
			'startAngle' : p.angle + p.angles[0] - 90,
			'endAngle' :p.angle + p.angles[0] - 10,
			'id' : 'outsideEndArcL'
		})
		insideEndArcL = Arc({
			'startPoint' : '%outsideEndArcL.startPoint',
			'radius' : '%outsideEndArcL.radius',
			'startAngle' : '%outsideEndArcL.startAngle+180',
			'endAngle' : '%startAngle-80',
			'reverse' : True,
			'id' : 'insideEndArcL'
		})
		mainArcL = Arc({
			'startPoint' : '%startArcL.endPoint',
			'endPoint' : '%outsideEndArcL.endPoint',
			'startAngle' : p.angle - 100
		})
		self.addSubShape(startArcL)
		self.addSubShape(outsideEndArcL)
		self.addSubShape(insideEndArcL)
		self.addSubShape(mainArcL)
		startArcR = Arc({
			'startPoint' : p.startPoint,
			'radius' : 0.1 * p.baseRadius * p.featureScaling,
			'startAngle' : p.angle + 80,
			'endAngle' : p.angle + 10,
			'id' : 'startArcR',
			'reverse' : True
		})
		outsideEndArcR = Arc({
			'startPoint' : subtractVectors(p.endPoints[1], transformPoint((p.baseLength * p.lengthScaling * 0.05, 0), angle = p.angle + p.angles[1])),
			'radius' : 0.11 * p.baseRadius * p.featureScaling * p.featureScalingFactor[1],
			'startAngle' : p.angle + p.angles[1] + 90,
			'endAngle' :p.angle + p.angles[1] -+ 10,
			'id' : 'outsideEndArcR',
			'reverse' : True
		})
		insideEndArcR = Arc({
			'startPoint' : '%outsideEndArcR.startPoint',
			'radius' : '%outsideEndArcR.radius',
			'startAngle' : '%outsideEndArcR.startAngle+180',
			'endAngle' : '%startAngle+80',
			'id' : 'insideEndArcR'
		})
		mainArcR = Arc({
			'startPoint' : '%startArcR.endPoint',
			'endPoint' : '%outsideEndArcR.endPoint',
			'startAngle' : p.angle + 100,
			'reverse' : True
		})
		self.addSubShape(startArcR)
		self.addSubShape(outsideEndArcR)
		self.addSubShape(insideEndArcR)
		self.addSubShape(mainArcR)
		topArc = Arc({
			'startPoint' : '%insideEndArcL.endPoint',
			'endPoint' : '%insideEndArcR.endPoint',
			'startAngle' : p.angle - 30
		})
		self.addSubShape(topArc)

class TwoHoleChains(Shape):
	defaultParams = {
		'baseLength' : 10,
		'baseRadius' : 0.9,
		'holeRadiiFactors' : [0.5, 0.3, 0.4, 1],
	}
	def __init__(self, treeData, params):
		self.crossesLimit = False
		Shape.__init__(self, params)
		p = self.p
		angles = [
			p.angle + p.angles[0] * 0.5,
			p.angle + p.angles[1] * 0.5
		]
		endPoints = [
			addVectors(transformPoint((p.baseLength * p.lengthScaling, 0), angles[0]), p.startPoint),
			addVectors(transformPoint((p.baseLength * p.lengthScaling, 0), angles[1]), p.startPoint),
		]
		limitLineStartPoint = addVectors(p.startPoint, transformPoint((0.05 * p.baseLength * p.lengthScaling, 0), p.angle))
		for endPoint in endPoints:
			for limitLine in treeData['limitLines']:
				if linesCross(limitLine, (limitLineStartPoint, endPoint)):
					self.crossesLimit = True
				else:
					if linesCross((limitLineStartPoint, endPoint), limitLine):
						# self.crossesLimit = True
						pass
						# print (p.startPoint, endPoint)
						# print limitLine
						# print ''
		if not self.crossesLimit:
			offsetVector = (p.baseLength * p.featureScaling * 0.08, p.baseLength * p.featureScaling * 0.03)
			mainArcL = Arc({
				'startPoint' : addVectors(p.startPoint, transformPoint(offsetVector, angle = p.angle)),
				'endPoint' : endPoints[0],
				'startAngle' : p.angle - 85
			})
			offsetVector = (p.baseLength * p.featureScaling * 0.08, -p.baseLength * p.featureScaling * 0.03)
			mainArcR = Arc({
				'startPoint' : addVectors(p.startPoint, transformPoint(offsetVector, angle = p.angle)),
				'endPoint' : endPoints[1],
				'startAngle' : p.angle + 85,
				'reverse' : True
			})
			# radius = p.baseRadius * p.featureScaling
			# holeRadii = [radius * factor for factor in p.holeRadiiFactors]
			# holeDistance = p.baseRadius * p.featureScaling
			# holesL = HolesOnArcChain(ShapeGroup('L', mainArcL), {
				# 'holeRadii' : holeRadii,
				# 'holeDistance' :holeDistance,
				# 'minRadius' : 0.06
			# })
			self.addSubShape(mainArcL)
			# holesR = HolesOnArcChain(ShapeGroup('R', mainArcR), {
				# 'holeRadii' : holeRadii,
				# 'holeDistance' :holeDistance, 
				# 'minRadius' : 0.06
			# })
			self.addSubShape(mainArcR)
			# mainArcL.calculate()
			# mainArcR.calculate()
			p.endPoints = endPoints
			
			if p.endNodeRadius:
				for i in [0, 1]:
					self.addSubShape(Circle({
						'centerPoint' : p.endPoints[i],
						'radius' : p.endNodeRadius * p.secondaryFeatureScaling
					}))
					self.addSubShape(Circle({
						'centerPoint' : p.endPoints[i],
						'radius' : p.endNodeRadius * p.secondaryFeatureScaling * 0.75
					}))
			treeData['limitLines'] += [(p.startPoint, p.endPoints[0]), (p.startPoint, p.endPoints[1])]
			# if len(holesL.subShapes) > 3:
				# treeData['limitLines'].append((holesL.subShapes[-1].p.centerPoint, holesR.subShapes[-1].p.centerPoint))

class BranchingShapeElement(Shape):
	defaultParams = {
		'lengthScaling' : 1,
		'featureScaling' : 1,
		'secondaryFeatureScaling' : 1,
		'angle' : 90,
		'depth' : 0,
		'maxDepth' : 6,
		'angles' : [80, -80],
		'directionalitySum' : 0,
		'featureScalingFactor' : [0.75, 0.75, 0.75],
		'secondaryFeatureScalingFactor' : [0.75, 0.75, 0.75],
		'lengthScalingFactor' : [0.75, 0.75, 0.75],
		'minLengthScaling' : 0.1,
		'minFeatureScaling' : 0.1,
		'directionalityAngleAdjustmentExponent' : 1.7,
		'directionalityAngleAdjustmentFactor' : 0,
		'distanceLimitingFactor' : 1.0,
		'skipPercentage' : 0,
	}
	def __init__(self, branchClass, treeData, *args):
		Shape.__init__(self, *args)
		paramVals = {k : self.p[k].value for k in self.p.keys()}
		branchShape = branchClass(treeData, paramVals)
		if not branchShape.crossesLimit:
			self.addSubShape(branchShape)
			p = self.p 
			existingEndPoints = copy(treeData['endPoints'])
			treeData['endPoints'] += [(endPoint, branchShape.p.lengthScaling) for endPoint in branchShape.p.endPoints]
			treeData['endPoints'].append((branchShape.p.startPoint, branchShape.p.lengthScaling))
			if p.depth < p.maxDepth and p.lengthScaling > p.minLengthScaling and p.featureScaling > p.minFeatureScaling: 
				for i in range(len(p.angles)):
					if existingEndPoints:
						closestDistance = min([distanceBetween(branchShape.p.endPoints[i], existingEndPoint[0]) * pow(existingEndPoint[1], 1.2) for existingEndPoint in existingEndPoints])
					else:
						closestDistance = branchShape.p.baseLength
					allowableClosestDistance = branchShape.p.baseLength * branchShape.p.lengthScaling * p.lengthScalingFactor[i] * p.distanceLimitingFactor * pow(p.exponentialDistanceLimitingFactor, p.depth)
					if closestDistance > allowableClosestDistance and 100 * random() > p.skipPercentage:
						directionalityIncrement = float(len(p.angles) - 1) / 2 - float(i)
						directionalityAngleAdjustment = pow(abs(p.directionalitySum), p.directionalityAngleAdjustmentExponent) * p.directionalityAngleAdjustmentFactor
						if p.directionalitySum < 0:
							directionalityAngleAdjustment =-directionalityAngleAdjustment
						newParamVals = copy(paramVals)
						newParamVals['lengthScaling'] *= p.lengthScalingFactor[i] 
						newParamVals['featureScaling'] *= p.featureScalingFactor[i]
						newParamVals['secondaryFeatureScaling'] *= p.secondaryFeatureScalingFactor[i]
						newParamVals['angle'] = p.angle + directionalityAngleAdjustment + p.angles[i]
						newParamVals['depth'] = p.depth + 1
						newParamVals['startPoint'] = branchShape.p.endPoints[i]
						newParamVals['directionalitySum'] += directionalityIncrement
						self.addSubShape(BranchingShapeElement(branchClass, treeData, newParamVals))

class Lines2(Shape):
	defaultParams = {
		'baseLength' : 10,
		'branchAngles' : [60, -60],
	}
	def __init__(self, treeData, params):
		Shape.__init__(self, params)
		def addLine(startPoint, endPoint):
			crossesExisting = False
			for existingLine in treeData['lines']:
				if linesCross(existingLine, (startPoint, endPoint), 0.0001) or linesCross((startPoint, endPoint), existingLine, 0.0001):
					crossesExisting = True
					continue
			if not crossesExisting:
				treeData['lines'].append((startPoint, endPoint))
				self.addSubShape(Line({'startPoint' : startPoint, 'endPoint' : endPoint}))
			return not crossesExisting
		mainLength = 1 * self.p.lengthScaling * self.p.baseLength
		branchLength = 0 * self.p.lengthScaling * self.p.baseLength
		forkingPoint = addVectors(transformPoint((mainLength, 0), self.p.angle), self.p.startPoint)
		endPoints = []
		if not 'lines' in treeData.keys():
			treeData['lines'] = []
		if addLine(self.p.startPoint, forkingPoint):
			for i in range(len(self.p.branchAngles)):
				endPoint = addVectors(transformPoint((branchLength, 0), self.p.angle + self.p.branchAngles[i]), forkingPoint)
				if addLine(forkingPoint, endPoint):
					endPoints.append(endPoint)
		self.crossesLimit = len(endPoints) == 0
		self.p.endPoints = endPoints


class BranchingShape(Shape):
	def __init__(self, branchClass, *args):
		Shape.__init__(self, *args)
		treeData = {
			'endPoints' : [],
			'limitLines' : []
		}
		if self.p.limitLines:
			treeData['limitLines'] = self.p.limitLines
		self.addSubShape(BranchingShapeElement(branchClass, treeData, self.p.dumpValues())) 


class BranchingOutlinedShape(Shape):
	def __init__(self, branchClass, *args):
		Shape.__init__(self, *args)
		treeData = {
			'endPoints' : [],
			'limitLines' : []
		}
		if self.p.limitLines:
			treeData['limitLines'] = self.p.limitLines
		self.addSubShape(BranchingShapeElement(branchClass, treeData, self.p.dumpValues())) 
		# for limitLine in treeData['limitLines']:
			# self.addSubShape(Line({'startPoint' : limitLine[0], 'endPoint' : limitLine[1]}))