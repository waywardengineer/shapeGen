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
			'maxDepth' : 8,
			'angles' : [60, 0],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.6, 1, 0.6],
			'lengthScalingFactor' : [0.48, 0.85, 0.35],
			'minLengthScaling' : 0.01,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 1.6,
			'directionalityAngleAdjustmentFactor' : 8,
			'distanceLimitingFactor' : 0.2
		})
		topShape = ShapeGroup('topshape', trace, trace.getTransformedCopy(angle = 120), trace.getTransformedCopy(angle = 240))
		self.shapes.append(topShape)
		Design.build(self)
