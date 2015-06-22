from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):

	# def build(self):
		# self.shapes = []
		# tree = BranchingShape(CirclesAtNodes, {
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
		# topShape = ShapeGroup('topshape', tree) 
		# self.shapes.append(topShape)
		# Design.build(self)
		
	def build(self):
		self.shapes = []
		lengthRatios = [0.5, 0.5, 0.7]
		topShape = ShapeGroup('topshape')
		holeDistance = 0.22
		for sizeIndex in range(3):
			topX = sizeIndex ** 1.5 * 0.3
			topY = sizeIndex * 0.4
			size = sizeIndex * 2 + 3.5
			holeRadii = [0.08, 0.08 + sizeIndex * 0.003, 0.08 + sizeIndex * 0.005, 0.08 + sizeIndex * 0.02, 0.08]
			lSide = ArcChain('lSide', [{
				'startPoint' : (0, 0),
				'startAngle' : 15,
				'endAngle' : 55,
				'radius' : size * lengthRatios[0]
			},{
				'angleSpan' : 33,
				'radius' : size * lengthRatios[1],
			},
			{
				'endPoint' : (-topX, size * lengthRatios[2] + topY),
				'noDirectionAlternate' : True
			}])
			rSide = ArcChain('rSide', [{
				'startPoint' : (0, 0),
				'startAngle' : 165,
				'endAngle' : 125,
				'radius' : size * lengthRatios[0],
				'reverse' : True
			},{
				'angleSpan' : 33,
				'radius' : size * lengthRatios[1],
			},
			{
				'endPoint' : (topX, size * lengthRatios[2] + topY),
				'noDirectionAlternate' : True
			}])
			heart = ShapeGroup('heart' + str(size), 
				HolesOnArcChain(lSide, {
					'holeDistance' : holeDistance, 
					'holeRadii' : holeRadii,
					'minRadius' : 0.08,
					'id' : 'lHoles'
				}),
				HolesOnArcChain(rSide, {
					'holeDistance' : holeDistance, 
					'holeRadii' : holeRadii,
					'minRadius' : 0.08,
					'id' : 'rHoles'
				}),
			)
			heart.transform(distance=(0, - sizeIndex * 0.7))
			topShape.addSubShape(heart)
		spiral = HolesOnArcChain( 
			ArcChain('spiral', [{
					'rotationAngle' : 0,
					'centerPoint' : (7, 0),
					'scaleFactor' : 0.4,
					'growthFactorAdjustment' : 0.5,
					'sweepAngleSpan' : 400,
					'reverse' : True
				}]), {
				'holeDistance' : holeDistance, 
				'holeRadii' : holeRadii,
				'minRadius' : 0.08,
				'id' : 'lHoles'
			}
		)
		topShape.addSubShape(spiral)
		self.shapes.append(topShape)
		Design.build(self)
