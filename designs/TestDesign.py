from .DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):

		
	def build(self):
		self.shapes = []
		arc = Arc({
			'startPoint' : (0, -1),
			'endPoint' : (1, 0),
			'radius' : 0.8,
			'id' : 'arc1'
		})
		xLine = Line({
			'startPoint' : (0, 0),
			'endPoint' : (5, 0)
		})
		yLine = Line({
			'startPoint' : (0, 0),
			'endPoint' : (0, 5)
		})
		circle = Circle({
			'centerPoint' : '%arc1.centerPoint',
			'radius' : 0.1
		})
		topShape = ShapeGroup('top', arc, xLine, yLine, circle)
		self.shapes.append(topShape)
		Design.build(self)



