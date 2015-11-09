from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):

		
	def build(self):
		self.shapes = []
		innerSpiral = Spiral({
			'rotationAngle' : 0,
			'sweepStartAngle' : 0,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.4,
			'growthFactorAdjustment' : 0.4,
			'sweepAngleSpan' : 720,
			'reverse' : True,
			'id' : 'innerSpiral'
		})
		outerSpiral = Spiral({
			'rotationAngle' : 0,
			'sweepStartAngle' : 0,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.7,
			'growthFactorAdjustment' : 0.45,
			'sweepAngleSpan' : 720,
			'reverse' : True,
			'id' : 'outerSpiral'
		})
		topShape = ShapeGroup('top', innerSpiral, outerSpiral)
		self.shapes.append(topShape)
		Design.build(self)



