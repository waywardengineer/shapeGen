from .DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *


class branchThing(Design):
	def build(self):
		w1 = Lines({
			'startPoint': (0, 0),
			'length': 0.1,
			'featureSize': 1.5,
			'angle': 90,
			'maxDepth': 80,
			'angles': [1, 35],
			'lengthFactor': [0.995, 0.5],
			'branchIntervals': [None, 8, 8],
			'branchIntervalOffsets': [None, 0, 4],
			'minLength': 0.004,
			'minBranchingDepth': 40,
			'directionalityExponent': 0.4,
			'directionalityFactor': -1,
			'depthExponent': 0.7,
			'depthFactor': 0.3,
			'distanceLimitingFactor': 0.2,
			'skipPercentage': 0,
		})
		topShape = ShapeGroup(
			'topshape', w1
		)
		self.shapes = []
		self.shapes.append(topShape)
		Design.build(self)

class Wing(Design):
	def build(self):
		w1 = Lines({
			'startPoint': (0, 0),
			'length': 0.1,
			'featureSize': 1.5,
			'angle': 0,
			'maxDepth': 80,
			'angles': [25, 0],
			'featureSizeFactor': [0.8, 0.9],
			'lengthFactor': [0.995, 0.33],
			'branchIntervals': [None, 8],
			'branchIntervalOffsets': [None, 0],
			'minLength': 0.004,
			'minBranchingDepth': 10,
			'directionalityExponent': 0.6,
			'directionalityFactor': 0,
			'depthExponent': 0.25,
			'depthFactor': -12,
			'distanceLimitingFactor': 0.2,
			'skipPercentage': 0,
		})
		w2 = Lines({
			'startPoint': (2, 0),
			'length': 0.1,
			'featureSize': 1.5,
			'angle': 0,
			'maxDepth': 80,
			'angles': [25, 0],
			'featureSizeFactor': [0.8, 0.9],
			'lengthFactor': [0.995, 0.33],
			'branchIntervals': [None, 8],
			'branchIntervalOffsets': [None, 0],
			'minLength': 0.004,
			'minBranchingDepth': 10,
			'directionalityExponent': 0.6,
			'directionalityFactor': 0,
			'depthExponent': 0.24,
			'depthFactor': -12,
			'distanceLimitingFactor': 0.2,
			'skipPercentage': 0,
		})
		topShape = ShapeGroup(
			'topshape', w2
		)
		self.shapes.append(topShape)
		Design.build(self)

class HeartHalf(Design):
	def build(self):
		inner = Lines({
			'startPoint': (0, 0),
			'length': 0.12,
			'featureSize': 1,
			'angle': -30,
			'maxDepth': 87,
			'angles': [28, 0],
			'featureSizeFactor': [0.8, 0.9],
			'lengthFactor': [0.995, 0.33],
			'branchIntervals': [None, 8],
			'branchIntervalOffsets': [None, 0],
			'minLength': 0.002,
			'minBranchingDepth': 20,
			'directionalityExponent': 0.6,
			'directionalityFactor': 0,
			'depthExponent': 0.26,
			'depthFactor': -12.2,
			'distanceLimitingFactor': 0.2,
			'skipPercentage': 0,
		})
		topShape = ShapeGroup(
			'topshape', inner
		)
		self.shapes.append(topShape)
		Design.build(self)





class Chand2x(Design):
	def build(self):
		self.shapes = []
		commonParams = {
			'maxDepth': 3,
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


