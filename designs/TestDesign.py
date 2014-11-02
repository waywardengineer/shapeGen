from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):
	# def build(self):
		# circle = Circle({
			# 'centerPoint' : (0, 0),
			# 'radius' : 2.5
		
		# })
		# arcChain = ArcChain( 'arcChain', [{
			# 'rotationAngle' : 0,
			# 'centerPoint' : (0, 0),
			# 'scaleFactor' : 0.04,
			# 'growthFactorAdjustment' : 0.75,
			# 'sweepAngleSpan' : 1000,
			# 'reverse' : False,
			# 'id' : 'spiral4'
		# }])
		# holes = HolesOnArcChain(arcChain,{
			# 'holeDistance' : 0.2, 
			# 'holeRadii' : [0.001, 0.01, 0.2, 0.3],
			# 'minRadius' : 0.06,
		# })
		# spiral = Spiral({
			# 'rotationAngle' : 0,
			# 'centerPoint' : (0, 0),
			# 'scaleFactor' : 0.04,
			# 'growthFactorAdjustment' : 0.80,
			# 'sweepAngleSpan' : 1000,
			# 'reverse' : False,
			# 'id' : 'spiral4'

		# })
		# topShape = ShapeGroup('topshape', spiral, spiral.getTransformedCopy(angle = 120), spiral.getTransformedCopy(angle = 240), )
		# self.shapes.append(topShape)
		# Design.build(self)

	def build(self):
		self.shapes = []
		trace = BranchingShape(Branch2, {
			'startPoint' : (0, 0),
			'lengthScaling' : 1,
			'featureScaling' : 1,
			'angle' : 90,
			'depth' : 0,
			'maxDepth' : 12,
			'angles' : [70, -70],
			'directionalitySum' : 0,
			'featureScalingFactor' : [0.9, 0.9],
			'lengthScalingFactor' : [0.8, 0.8],
			'minLengthScaling' : 0.1,
			'minFeatureScaling' : 0.1,
			'directionalityAngleAdjustmentExponent' : 1.6,
			'directionalityAngleAdjustmentFactor' : 2,
			'distanceLimitingFactor' : 0.08,
			'skipPercentage' : 25,
			'baseRadius' : 0.9,
			'holeRadiiFactors' : [0.2, 0.3, 0.4, 1],
			'baseLength' : 22.5,
			'exponentialDistanceLimitingFactor' : 1.1

		})
		topShape = ShapeGroup('topshape', trace) 
		self.shapes.append(topShape)
		Design.build(self)
		
	# def build(self):
		# trace = BranchingShape(CircleNodes, {
			# 'startPoint' : (0, 0),
			# 'lengthScaling' : 1.1,
			# 'featureScaling' : 2,
			# 'angle' : 90,
			# 'depth' : 0,
			# 'maxDepth' : 8,
			# 'angles' : [60, 0],
			# 'directionalitySum' : 0,
			# 'featureScalingFactor' : [0.6, 1, 0.6],
			# 'lengthScalingFactor' : [0.48, 0.85, 0.35],
			# 'minLengthScaling' : 0.01,
			# 'minFeatureScaling' : 0.1,
			# 'directionalityAngleAdjustmentExponent' : 1.6,
			# 'directionalityAngleAdjustmentFactor' : 8,
			# 'distanceLimitingFactor' : 0.2
		# })
		# topShape = ShapeGroup('topshape', trace, trace.getTransformedCopy(angle = 120), trace.getTransformedCopy(angle = 240))
		# self.shapes.append(topShape)
		# Design.build(self)

