from dxfwrite import DXFEngine as dxf
from shapes import *


class Design(object):
	def __init__(self):
		self.fileName = 'output.dxf'
		self.params = {}
		self.shapes = []
	def saveToFile(self):
		self.drawing = dxf.drawing(self.fileName)
		self.addShapes()
		for shape in self.shapes:
			shape.addToDrawing(self.drawing)
		self.drawing.save()
	def getDrawingContents(self):
		self.saveToFile()
		with open (self.fileName, "r") as file:
			data = file.read()
		return data
	def getCurrentStateData(self):
		data = {'drawingContents' : self.getDrawingContents(), 'params' : self.params}
		return data
	def addShapes(self):
		self.shapes = []
	def updateValue(self, param, value):
		self.params[param] = value

class TestDesign(Design):
	def __init__(self):
		Design.__init__(self)
		self.params = {
			'arc1StartAngle' : 240,
			'arc1EndAngle' : 350,
		}
	def addShapes(self):
		Design.addShapes(self)
		arc1 = Arc({
			'startPoint' : (0, 0),
			'startAngle' : self.params['arc1StartAngle'],
			'endAngle' : self.params['arc1EndAngle'],
			'radius' : 2
		})
		arc2 = Arc({
			'startPoint' : arc1.params['endPoint'],
			'startAngle' : arc1.params['endAngle'] + 180,
			'radius' : 8,
			'endAngle' : 60,
			'reverse' : True
		})
		arcs = ShapeGroup(arc1, arc2)
		arcs2 = arcs.getTransformedCopy(angle = -20)
		arcsGroup = ShapeGroup(
			arcs, arcs2
		)
		arc3 = Arc({
			'startPoint' : arcs2.subShapes[1].params['endPoint'],
			'startAngle' : arcs2.subShapes[1].params['endAngle'] + 180,
			'radius' : 8,
			'endAngle' : 300,
			'reverse' : False
		})
		armGroup = ShapeGroup(arcsGroup, arc3)
		armGroup.transform(distance = (-(arc3.params['endPoint'][0] + 2), -(arc3.params['endPoint'][1] + 1)))
		mainGroup = ShapeGroup(armGroup, armGroup.getTransformedCopy(angle = 120),  armGroup.getTransformedCopy(angle = 240))
		self.shapes.append(mainGroup)
