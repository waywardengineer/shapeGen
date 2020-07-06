from .DesignBase import Design
from shapes import *
import json


class HoleySpiralArm(Design):
	def build(self):
		self.shapes = []
		spiral = Spiral({
			'rotationAngle' : 45, 
			'centerPoint' : (0,0), 
			'sweepAngleSpan' : 420, 
			'scaleFactor' : 0.5, 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'spiral.endPoint',
			'startAngle' : 'spiral.endAngle+180',
			'endAngle' : 'spiral.endAngle+250',
			'radius' : 4,
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'arc1.endPoint',
			'startAngle' : 'arc1.endAngle+180',
			'radius' : 5,
			'endAngle' : 'arc1.endAngle+100',
			'reverse' : True,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		middleCurve = ShapeGroup('middleCurve', spiral, arc1, arc2)

		spiral = Spiral({
			'rotationAngle' : 'middleCurve.spiral.rotationAngle', 
			'centerPoint' : (0,0), 
			'sweepAngleSpan' : 'middleCurve.spiral.sweepAngleSpan', 
			'scaleFactor' : 'middleCurve.spiral.scaleFactor*1.2', 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'spiral.endPoint',
			'startAngle' : 'spiral.endAngle+180',
			'endAngle' : 'spiral.endAngle+250',
			'radius' : 'middleCurve.arc1.radius*0.7',
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'arc1.endPoint',
			'startAngle' : 'arc1.endAngle+180',
			'radius' : 'middleCurve.arc2.radius*1.4',
			'endAngle' : 'arc1.endAngle+120',
			'reverse' : True,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		outerCurve = ShapeGroup('outerCurve', spiral, arc1, arc2)

		spiral = Spiral({
			'rotationAngle' : 'middleCurve.spiral.rotationAngle', 
			'centerPoint' : (0,0), 
			'sweepAngleSpan' : 'middleCurve.spiral.sweepAngleSpan+30', 
			'scaleFactor' : 'middleCurve.spiral.scaleFactor*0.8', 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'spiral.endPoint',
			'startAngle' : 'spiral.endAngle+180',
			'endAngle' : 'spiral.endAngle+250',
			'radius' : 'middleCurve.arc1.radius*1.2',
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'arc1.endPoint',
			'startAngle' : 'arc1.endAngle+180',
			'radius' : 'middleCurve.arc2.radius*0.8',
			'endAngle' : 'arc1.endAngle+100',
			'reverse' : True,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		innerCurve = ShapeGroup('innerCurve', spiral, arc1, arc2)
		holes = HolesOnArcChain(middleCurve, {
			'holeDistance' : 0.125, 
			'holeRadii' : [0.125, 0.25, 1, 0.5],
			'id' : 'holeChain',
			'changeableParams' : ['holeDistance']
		})
		topShape = ShapeGroup('top', innerCurve, holes, outerCurve, middleCurve)
		middleCurve.updateParam('excludeSubShapes', True)
		self.shapes.append(topShape)
		Design.build(self)
