from DesignBase import Design
from shapes import *
import json


class ThreeSidedPointyThing(Design):
	def build(self):
		self.shapes = []
		arcChain = ArcChain('arcChain', [{
			'startPoint' : (0, 0),
			'startAngle' : 120, 
			'angleSpan' : 30, 
			'radius' : 5,
			'reverse' : True,
			#'changeableParams' : ['radius', 'angleSpan'],
		},{
			'angleSpan' : 60,
			'radius' :5,
			#'changeableParams' : ['radius', 'angleSpan'],
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		},{
			'angleSpan' : 60,
			'radius' : 'arc1.radius',
		},{
			'angleSpan' : 30,
			'radius' : 'arc0.radius',
		}])
		arcChainForHoles = ArcChain('arcChainForHoles', [{
			'startAngle' : 'oneEdge.arcChain.arc2.startAngle + 5', 
			'endAngle' : 'oneEdge.arcChain.arc2.endAngle - 5', 
			'centerPoint' : 'oneEdge.arcChain.arc2.centerPoint',
			'radius' : 'oneEdge.arcChain.arc2.radius - 0.75',
			'reverse' : True,
			'changeableParams' : ['radius', 'startAngle', 'endAngle'],
		},{
			'angleSpan' : 60,
			'radius' :4.5,
			'changeableParams' : ['radius', 'angleSpan'],
		},{
			'angleSpan' : 25,
			'radius' :2,
			'changeableParams' : ['radius', 'angleSpan'],
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 50,
			'radius' : 'arc1.radius',
			'prepend' : True
		}])
		spiral = Spiral({
			'rotationAngle' : 45, 
			'centerPoint' : (0,0), 
			'sweepAngleSpan' : 420, 
			'scaleFactor' : 0.25, 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		holes = HolesOnArcChain(arcChainForHoles, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.2, 0.4, 0.125, 0.4, 0.2],
			# 'id' : 'holeChain'
		})

		endArc = Arc({
			'startPoint' : (0, 0),
			'startAngle' : 110,
			'endAngle' : 250,
			'radius' : 3,
			'reverse' : True,
			'id' : 'endArc'
		})
		circle = Circle({
			'centerPoint' : 'oneEdge.arcChain.arc2.centerPoint',
			'radius' : 1,
			#'changeableParams' : ['radius'],
			'id' : 'circle'
		})

		oneEdge = ShapeChain('oneEdge', (endArc, 'es'), (arcChain, 'se'))
		oneSide = ShapeGroup('oneSide', oneEdge, circle, holes)
		sides = ShapeChain('sides', (oneSide, 'es'), (oneSide.getTransformedCopy(angle=120), 'es'), (oneSide.getTransformedCopy(angle=240), 'es'))
		topShape = ShapeGroup('top', sides)
		# sides.s.b.s.b.updateParam('radius', 'oneSide.circle.radius*1.2')
		# sides.s.c.s.b.updateParam('radius', 'oneSide.circle.radius*1.5')
		# for angle in range(0, 360, 30):
			# topShape.subShapes.append(holes.getTransformedCopy(angle = angle))
		self.shapes.append(topShape)
		Design.build(self)