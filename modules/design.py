from dxfwrite import DXFEngine as dxf
from shapes import *
import json

class Design(object):
	def __init__(self):
		self.fileName = 'output.dxf'
		self.paramDirectory = {}
		self.modifiedParams = {}
		self.shapes = []
	def saveToFile(self):
		self.drawing = dxf.drawing(self.fileName)
		self.build()
		for shape in self.shapes:
			shape.addToDrawing(self.drawing)
		self.drawing.save()
	def getDrawingContents(self):
		self.saveToFile()
		with open (self.fileName, "r") as file:
			data = file.read()
		return data
	def getCurrentStateData(self):
		drawingContents = self.getDrawingContents()
		paramDataList = []
		for id in self.paramDirectory.keys():
			item = self.paramDirectory[id]
			paramDataList += [{'id' : id + ':' + k, 'value' : item['object'].params[k]} for k in item['changeableParams']]
		data = {
			'drawingContents' : drawingContents,
			'params' : {i['id'] : i['value'] for i in paramDataList} 
		}
		return data
	def build(self):
		paramDirectoryList = []
		for shape in self.shapes:
			paramDirectoryList += shape.getParamDirectory()
		self.paramDirectory = {d['id'] : d for d in paramDirectoryList}
		for id in self.modifiedParams.keys():
			(objectId, paramId) = id.split(':')
			self.paramDirectory[objectId]['object'].updateParam(paramId, self.modifiedParams[id])
		for shape in self.shapes:
			shape.build()
			
	def updateValue(self, id, value):
		self.modifiedParams[id] = value

class TestDesign(Design):
	def build(self):
		self.shapes = []
		spiral = Spiral({
			'startAngle' : 45, 
			'centerPoint' : (0,0), 
			'angleSpan' : 420, 
			'scaleFactor' : 5, 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : (0, 0),
			'startAngle' : 135,
			'endAngle' : 45,
			'radius' : 20,
			'reverse' : True,
			'id' : 'arc1',
			'changeableParams' : ['startAngle']
		})
		arc2 = Arc({
			'startPoint' : 'any.spiral.endPoint',
			'startAngle' : 'any.spiral.endAngle+180',
			'radius' : 20,
			'endAngle' : 20,
			'reverse' : False,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		arcs = ShapeGroup('curve', spiral, arc2)
		holes = HolesOnArcChain(arcs, {
			'holeDistance' : 1, 
			'holeRadii' : [0.5, 1, 3, 0.5],
			'id' : 'holeChain',
			'changeableParams' : ['holeDistance']
		})
		bezCurve = BezCurve({'points' : [
			((0, 0), 45, (1, 1)),
			((5, 0), 315, (1, 1)),
			((8, 2), 200, (5, 1))
		]})
		circle = Circle({'centerPoint' : (0, 0), 'radius' : 5})
		topShape = ShapeGroup('top', holes.getTransformedCopy(distance=(0, 10)))
		for angle in range(30, 360, 30):
			topShape.subShapes.append(holes.getTransformedCopy(angle = angle, distance=(0, 10)))
		self.shapes.append(topShape)
		Design.build(self)
