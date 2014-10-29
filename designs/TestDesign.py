from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):
	def build(self):
		trace = BranchingShape(BranchTest, {
			'startPoint' : (0, 0),
		})
		topShape = ShapeGroup('topshape', trace)
		self.shapes.append(topShape)
		Design.build(self)

