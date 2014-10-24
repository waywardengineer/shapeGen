from DesignBase import Design, MultiDesign
from shapes import *
import json
class MultiThree(MultiDesign):
	def __init__(self):
		self.designs = [ThreeArmThinSpiral(330-15*i, 0.2+0.025*i) for i in range(10)]
		MultiDesign.__init__(self)
		self.saveToFile()

class ThreeArmThinSpiral(Design):
	def __init__(self, spiralSweep=330, growthFactorDiff=0.2):
		Design.__init__(self)
		self.spiralSweep = spiralSweep
		self.growthFactorDiff=growthFactorDiff

	def build(self):
		self.shapes = []
		inner = ArcChain('inner', [{
			'rotationAngle' : self.spiralSweep-30,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.5,
			'growthFactorAdjustment' : 1.0 - self.growthFactorDiff/2,
			'sweepAngleSpan' : self.spiralSweep,
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :2.5,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		}])
		outer = ArcChain('outer', [{
			'rotationAngle' : 'inner.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : 'inner.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0 + self.growthFactorDiff/2,
			'sweepAngleSpan' : 'inner.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :2,
		}])
		holeChain = ArcChain('holeChain', [{
			'rotationAngle' : 'inner.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : 'inner.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0,
			'sweepAngleSpan' : 'inner.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 62,
			'radius' :2.2,
			'changeableParams' : ['radius'],
		},{
			'angleSpan' : 150,
			'radius' :3,
			'changeableParams' : ['radius', 'endAngle'],
		}])
		holes = HolesOnArcChain(holeChain, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0, 0.1, 0.25, 0.2, 0.01],
			'minRadius' : 0.125,
			'id' : 'hole'
		})
		side = ShapeGroup('side', inner, outer, holes)
		side.p.startPoint = 'outer.endPoint'
		side.p.endPoint = 'inner.endPoint'
		side2 = side.getTransformedCopy(angle = 120)
		side3 = side.getTransformedCopy(angle = 240)
		sides = ShapeChain('sides', (side, 'se'), (side2, 'se'), (side3, 'se'))
		circle = Circle({
			'centerPoint' : 'avgPoints ( side.inner.arc2.centerPoint , side1.inner.arc2.centerPoint , side2.inner.arc2.centerPoint )',
			'radius' : 2.5
		})
		spiral = Spiral({
			'rotationAngle' : 'side.inner.arc0.rotationAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : 'side.inner.arc0.scaleFactor',
			'growthFactorAdjustment' : 1.0,
			'sweepAngleSpan' : 'side.inner.arc0.sweepAngleSpan',
			'reverse' : True
		})
		topShape = ShapeGroup('top', sides, circle, spiral)
		self.shapes.append(topShape)
		Design.build(self)