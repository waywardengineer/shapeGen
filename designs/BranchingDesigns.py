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




class Something3(Design):
	def build(self):
		self.shapes = []
		commonParams = {
			'maxDepth': 6,
			'angles': [-50, 70],
			'featureSizeFactor': [1.0, 0.6],
			'featureSize': 2,
			'lengthFactor': [1.08, 0.8],
			'length': 5,
			'minLength': 0.1,
			'minFeatureSize': 0.6,
			'directionalityExponent': 0.8,
			'directionalityFactor': 1,
		}
		branch1Params = commonParams.copy()
		branch1Params.update({
			'featureSizeFactor': [1.0, 0.6],
			'featureSize': 2,
		})
		branch2Params = commonParams.copy()
		branch2Params.update({
			'featureSizeFactor': [0.97, 0.57],
			'featureSize': 2.8,
		})
		branch = HoneycombSpiral(branch1Params)
		branch2 = HoneycombSpiral(branch2Params)
		topShape = ShapeGroup(
			'topshape', 
			branch,
			branch2
		)
		self.shapes.append(topShape)
		Design.build(self)
		

class Chand2x(Design):
	def build(self):
		self.shapes = []
		commonParams = {
			'maxDepth': 1,
			'angles': [0, 55],
			'featureSize': 1,
			'featureSizeFactor': [1, 0.6],
			'length': 6,
			'lengthFactor': [0.91, 0.67],
			'minLength': 0.1,
			'minFeatureSize': 0.1,
			'directionalitySum': 1,
			'directionalityExponent': 0.6,
			'directionalityFactor': -20,
			'skipPercentage': 0,
		}
		branch1Params = commonParams.copy()
		branch1Params.update({
			'featureSizeFactor': [1.0, 0.6],
			'featureSize': 1,
		})
		branch2Params = commonParams.copy()
		branch2Params.update({
			'featureSizeFactor': [0.92, 0.57],
			'featureSize': 1.8,
		})
		branch1 = ChandBranch(branch1Params)
		branch2 = ChandBranch(branch2Params)
		topShape = ShapeGroup(
			'topshape', branch1, branch1.getTransformedCopy(angle=120), branch1.getTransformedCopy(angle=240),
			branch2, branch2.getTransformedCopy(angle=120), branch2.getTransformedCopy(angle=240)
		)
		self.shapes.append(topShape)
		Design.build(self)


class Chand2(Design):
	def build(self):
		self.shapes = []
		commonParams = {
			'maxDepth': 5 - self.sizeIndex,
			'angles': [0, 55],
			'featureSize': 1,
			'featureSizeFactor': [1, 0.6],
			'length': 6,
			'lengthFactor': [0.91, 0.67],
			'minLength': 0.1,
			'minFeatureSize': 0.1,
			'directionalitySum': 1,
			'directionalityExponent': 0.6,
			'directionalityFactor': -20,
			'skipPercentage': 0,
		}
		branch1Params = commonParams.copy()
		branch1Params.update({
			'featureSizeFactor': [1.0, 0.6],
			'featureSize': 1,
		})
		branch2Params = commonParams.copy()
		branch2Params.update({
			'featureSizeFactor': [0.92, 0.57],
			'featureSize': 1.8 * pow(0.92, self.sizeIndex),
		})
		branch1 = ChandBranch(branch1Params)
		branch2 = ChandBranch(branch2Params)
		topShape = ShapeGroup(
			'topshape', branch1, branch1.getTransformedCopy(angle=120), branch1.getTransformedCopy(angle=240),
			branch2, branch2.getTransformedCopy(angle=120), branch2.getTransformedCopy(angle=240)
		)
		self.shapes.append(topShape)
		Design.build(self)


