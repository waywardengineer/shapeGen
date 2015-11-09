from DesignBase import Design, MultiDesign
from shapes import *
import json

class ASpiral(Design):
	def __init__(self, sizeIndex=0):
		Design.__init__(self)
		self.sizeIndex = sizeIndex

	def build(self):
		spiralSweep = 330 - 15 * self.sizeIndex
		growthFactorDiff = 0.35 + 0.02 * self.sizeIndex
		self.shapes = []
		inner = ArcChain('inner', [{
			'rotationAngle' :  - 13 * self.sizeIndex,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.5 + 0.1 * self.sizeIndex,
			'growthFactorAdjustment' : 1.0 - growthFactorDiff/2,
			'sweepAngleSpan' : 330 + 90 - 13 * self.sizeIndex,
			'reverse' : True
		# },{
			# 'angleSpan' : 25 - 2 * self.sizeIndex,
			# 'radius' :3,
			# 'noDirectionAlternate' : True
		}])
		outer = ArcChain('outer', [{
			'rotationAngle' : '%inner.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : '%inner.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0 + growthFactorDiff / 2,
			'sweepAngleSpan' : 330 - 15 * self.sizeIndex,
			'reverse' : True
		},{
			'angleSpan' : 45,
			'radius' : 8,
		}])
		holeChain = ArcChain('holeChain', [{
			'rotationAngle' : '%outer.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : '%outer.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0,
			'sweepAngleSpan' : '%outer.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 41,
			'radius' : '%outer.arc1.radius * 1.2',
		}])
		holes = HolesOnArcChain(holeChain, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.03, 0.06, 0.3, 0.4, 0.6, 0.7, 0.8],
			'minRadius' : 0.045,
			'id' : 'hole'
		})
		side = ShapeGroup('side', inner, outer, holes)
		side.p.startPoint = '%outer.endPoint'
		side.p.endPoint = '%inner.endPoint'
		# hole = Circle({
			# 'centerPoint' : (3.9 + 0.065 * self.sizeIndex, 0),
			# 'radius' : 0.5 + 0.05 * self.sizeIndex
		# })
		# hole.transform(angle = 3 + 1.5 * self.sizeIndex)

		topShape = ShapeGroup(
			'top', 
			side, 
			# hole, hole.getTransformedCopy(angle = 120), 
			# hole.getTransformedCopy(angle = 240)
		)
		self.shapes.append(topShape)
		Design.build(self)
		
class ThreeArmThinSpiral(Design):
	def __init__(self, sizeIndex=0):
		Design.__init__(self)
		self.sizeIndex = sizeIndex

	def build(self):
		spiralSweep = 330 - 15 * self.sizeIndex
		growthFactorDiff = 0.25 + 0.02 * self.sizeIndex
		self.shapes = []
		inner = ArcChain('inner', [{
			'rotationAngle' :  - 13 * self.sizeIndex,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.5 + 0.1 * self.sizeIndex,
			'growthFactorAdjustment' : 1.0 - growthFactorDiff/2,
			'sweepAngleSpan' : 330 + 90 - 13 * self.sizeIndex,
			'reverse' : True
		# },{
			# 'angleSpan' : 25 - 2 * self.sizeIndex,
			# 'radius' :3,
			# 'noDirectionAlternate' : True
		}])
		outer = ArcChain('outer', [{
			'rotationAngle' : '%inner.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : '%inner.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0 + growthFactorDiff / 2,
			'sweepAngleSpan' : 330 - 15 * self.sizeIndex,
			'reverse' : True
		},{
			'angleSpan' : 45,
			'radius' : 8,
		}])
		holeChain = ArcChain('holeChain', [{
			'rotationAngle' : '%outer.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : '%outer.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0,
			'sweepAngleSpan' : '%outer.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 41,
			'radius' : '%outer.arc1.radius * 1.2',
		}])
		holes = HolesOnArcChain(holeChain, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.01, 0.01, 0.1, 0.25, 0.2, 0.3, 0.4],
			'minRadius' : 0.08,
			'id' : 'hole'
		})
		side = ShapeGroup('side', inner, outer, holes)
		side.p.startPoint = '%outer.endPoint'
		side.p.endPoint = '%inner.endPoint'
		side2 = side.getTransformedCopy(angle = 120)
		side3 = side.getTransformedCopy(angle = 240)
		sides = ShapeChain('sides', (side, 'se'), (side2, 'se'), (side3, 'se'))
		sides.transform(distance = 'subtractVectors ( ( 0 , 0 ) , avgPoints ( %side.inner.arc0.centerPoint , %side1.inner.arc0.centerPoint , %side2.inner.arc0.centerPoint ) )')
		circle = Circle({
			'centerPoint' : (0, 0),
			'radius' : 1.75,
			'id' : 'centerCircle'
		})
		# hole = Circle({
			# 'centerPoint' : (3.9 + 0.065 * self.sizeIndex, 0),
			# 'radius' : 0.5 + 0.05 * self.sizeIndex
		# })
		# hole.transform(angle = 3 + 1.5 * self.sizeIndex)

		topShape = ShapeGroup(
			'top', 
			sides, 
			circle,
			# hole, hole.getTransformedCopy(angle = 120), 
			# hole.getTransformedCopy(angle = 240)
		)
		self.shapes.append(topShape)
		Design.build(self)