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
		},{
			'angleSpan' : 60,
			'radius' :5,
		},{
			'angleSpan' : 60,
			'radius' : 3
		},{
			'angleSpan' : 60,
			'radius' : 'arc1.radius',
		},{
			'angleSpan' : 30,
			'radius' : 'arc0.radius',
		}])

		endArc = Arc({
			'startPoint' : (0, 0),
			'startAngle' : 110,
			'endAngle' : 250,
			'radius' : 3,
			'reverse' : True,
			'id' : 'endArc'
		})

		oneSide = ShapeChain('oneSide', (endArc, 'es'), (arcChain, 'se'))
		sides = ShapeChain('sides', (oneSide, 'es'), (oneSide.getTransformedCopy(angle=120), 'es'), (oneSide.getTransformedCopy(angle=240), 'es'))
		sides.transform(distance = 'subtractVectors ( ( 0 , 0 ) , avgPoints ( oneSide.endArc.centerPoint , oneSide1.endArc.centerPoint , oneSide2.endArc.centerPoint ) )')
		
		arcChainForHoles = ArcChain('arcChainForHoles', [{
			'rotationAngle' : 0,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.5,
			'growthFactorAdjustment' : 1.0,
			'sweepAngleSpan' : 360,
			'reverse' : True
		},{
			'angleSpan' : 25 ,
			'radius' : 5,
		},{
			'angleSpan' : 60 ,
			'radius' : 'oneSide.arcChain.arc2.radius - 0.75',
		},{
			'angleSpan' : 30,
			'radius' : 'oneSide.arcChain.arc3.radius + 0.75',
		},{
			'angleSpan' : 50,
			'radius' : 4,
			'noDirectionAlternate' : True
		}])
		holes = HolesOnArcChain(arcChainForHoles, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.1, 0.2, 0.125, 0.4, 0.2, 0.1],
			'id' : 'holeChain'
		})
		holes.transform(angle = 'oneSide.arcChain.arc2.startAngle - arc2.startAngle')
		holes.transform(distance = 'subtractVectors ( oneSide.arcChain.arc2.centerPoint , arc2.centerPoint )')
		sideHoles = ShapeGroup('sideHoles', holes, holes.getTransformedCopy(angle=120), holes.getTransformedCopy(angle=240))
		circle = Circle({
			'centerPoint' : 'oneSide.arcChain.arc2.centerPoint',
			'radius' : 1,
			'id' : 'circle'
		})
		topShape = ShapeGroup('top', sides, sideHoles, circle, circle.getTransformedCopy(angle=120), circle.getTransformedCopy(angle=240))
		self.shapes.append(topShape)
		Design.build(self)