from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class HeartVines(Design):
	def build(self):
		self.shapes = []
		trace = BranchingShape(TwoHoleChains, {
			'startPoint' : (36, 5),
			'lengthScaling' : 0.6,
			'featureScaling' : 0.6,
			'angle' : 90,
			'depth' : 0,
			'maxDepth' : 9,
			'angles' : [70, -70],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.9, 0.9],
			'lengthScalingFactor' : [0.8, 0.8],
			'minLengthScaling' : 0.05,
			'minFeatureScaling' : 0,
			'directionalityAngleAdjustmentExponent' : 1.6,
			'directionalityAngleAdjustmentFactor' : 2,
			'distanceLimitingFactor' : 0,
			'skipPercentage' : 15,
			'baseRadius' : 0.9,
			'holeRadiiFactors' : [0.5, 0.4, 0.6, 1],
			'baseLength' : 22.5,
			'exponentialDistanceLimitingFactor' : 1.1,
			'limitLines' : [((0, 0), (72, 0.1)), ((72, 0.1), (72.1, 36)), ((72.1, 36), (0.1, 36.1)), ((0.1, 36.1), (0, 0))]
		})
		topShape = ShapeGroup('topshape', trace) 
		self.shapes.append(topShape)
		Design.build(self)

class FerneyTree(Design):
	def build(self):
		trace = BranchingShape(CirclesAtNodes, {
			'startPoint' : (0, 0),
			'lengthScaling' : 1.1,
			'featureScaling' : 2,
			'angle' : 90,
			'depth' : 0,
			'maxDepth' : 7,
			'angles' : [60, 0],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.6, 1, 0.6],
			'lengthScalingFactor' : [0.48, 0.85, 0.35],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 1.6,
			'directionalityAngleAdjustmentFactor' : 8,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 0,
		})
		topShape = ShapeGroup('topshape', trace, trace.getTransformedCopy(angle = 120), trace.getTransformedCopy(angle = 240))
		self.shapes.append(topShape)
		Design.build(self)

class Something(Design):
	def build(self):
		self.shapes = []
		branch1 = BranchingShape(TwoHoleChains, {
			'startPoint' : (36, 0.5),
			'lengthScaling' : 1.5,
			'featureScaling' : 0.5,
			'secondaryFeatureScaling' : 0.5,
			'angle' : 90,
			'depth' : 0,
			'maxDepth' : 6,
			'angles' : [76, -76],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.83, 0.83],
			'secondaryFeatureScalingFactor' : [0.76, 0.76],
			'lengthScalingFactor' : [0.79, 0.79],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0,
			'directionalityAngleAdjustmentFactor' : 0,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 20,
			'baseRadius' : 1,
			'holeRadiiFactors' : [1.5, 1, 1.75],
			'endNodeRadius' : 4,
			'limitLines' : [((0, 0), (72, 0.1)), ((72, 0.1), (72.1, 54)), ((72.1, 54), (0.1, 54.1)), ((0.1, 54.1), (0, 0))]
			})
		branch2 = BranchingShape(CirclesAtNodes, {
			'startPoint' : (0, 0),
			'lengthScaling' : 0.5,
			'featureScaling' : 6.48,
			'angle' : 90,
			'maxDepth' : 3,
			'angles' : [55, 0],
			'featureScalingFactor' : [0.6, 0.9, 0.6],
			'lengthScalingFactor' : [0.62, 0.89, 0.35],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0.6,
			'directionalityAngleAdjustmentFactor' : 24,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 10,
		})
		topShape = ShapeGroup(
			'topshape', 
			branch1,
			# branch1.getTransformedCopy(angle = 120),
			# branch1.getTransformedCopy(angle = 240),
			# branch2, 
			# branch2.getTransformedCopy(angle = 120), 
			# branch2.getTransformedCopy(angle = 240)
		)
		self.shapes.append(topShape)
		Design.build(self)

class Something2(Design):
	def build(self):
		self.shapes = []
		branch = BranchingShape(Lines, {
			'startPoint' : (0, 0),
			'lengthScaling' : 0.7,
			'featureScaling' : 6.48,
			'angle' : 90,
			'maxDepth' : 12,
			'angles' : [-50, 70],
			'featureScalingFactor' : [1, 1],
			'lengthScalingFactor' : [1.15, 0.5],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0.8,
			'directionalityAngleAdjustmentFactor' : 1,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 10,
		})
		topShape = ShapeGroup(
			'topshape', 
			branch
		)
		self.shapes.append(topShape)
		Design.build(self)

class Something3(Design):
	def build(self):
		self.shapes = []
		branch = BranchingOutlinedShape(Lines2, {
			'startPoint' : (0, 0),
			'lengthScaling' : 0.7,
			'featureScaling' : 6.48,
			'angle' : 90,
			'maxDepth' : 12,
			'angles' : [-50, 70],
			'featureScalingFactor' : [1, 1],
			'lengthScalingFactor' : [1.15, 0.5],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0.8,
			'directionalityAngleAdjustmentFactor' : 1,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 10,
		})
		topShape = ShapeGroup(
			'topshape', 
			branch
		)
		self.shapes.append(topShape)
		Design.build(self)
		
class Chand1(Design):
	def build(self):
		branch1 = BranchingShape(CirclesAtNodes, {
			'startPoint' : (0, 0),
			'lengthScaling' : 0.5,
			'featureScaling' : 4,
			'angle' : 90,
			'depth' : 0,
			'maxDepth' : 5,
			'angles' : [55, 0],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.6, 1, 0.6],
			'lengthScalingFactor' : [0.62, 0.89, 0.35],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0.6,
			'directionalityAngleAdjustmentFactor' : 24,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 0,
		})
		branch2 = BranchingShape(CirclesAtNodes, {
			'startPoint' : (0, 0),
			'lengthScaling' : 0.5,
			'featureScaling' : 6.48,
			'angle' : 90,
			'maxDepth' : 3,
			'angles' : [55, 0],
			'featureScalingFactor' : [0.6, 0.9, 0.6],
			'lengthScalingFactor' : [0.62, 0.89, 0.35],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 0.6,
			'directionalityAngleAdjustmentFactor' : 24,
			'distanceLimitingFactor' : 0.2,
			'skipPercentage' : 0,
		})
		topShape = ShapeGroup(
			'topshape', branch1, branch1.getTransformedCopy(angle = 120), branch1.getTransformedCopy(angle = 240),
			branch2, branch2.getTransformedCopy(angle = 120), branch2.getTransformedCopy(angle = 240)
		)
		self.shapes.append(topShape)
		Design.build(self)
