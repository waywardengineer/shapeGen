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
		arcChain = ArcChain('arcChain', [{
			'startPoint' : (0, 0),
			'startAngle' : 120, 
			'angleSpan' : 30, 
			'radius' : 5,
			'reverse' : True,
		},{
			'angleSpan' : 60,
			'radius' :5
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		},{
			'angleSpan' : 60,
			'radius' : 5,
		},{
			'angleSpan' : 30,
			'radius' : 5,
		}])
		holes = HolesOnArcChain(arcChain, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.125, 0.5, 1, 0.125],
			'id' : 'holeChain'
		})
		endArc = Arc({
			'startPoint' : (0, 0),
			'startAngle' : 90,
			'endAngle' : 270,
			'radius' : 3,
			'reverse' : True,
			'id' : 'endArc'
		})
		circle = Circle({
			'centerPoint' : 'parent.arcChain.arc2.centerPoint',
			'radius' : 1
		})
		oneSide = ShapeGroup('oneSide', arcChain, endArc)
		#sideTwo = oneSide.getTransformedCopy(angle=120)
		sides = ShapeChain('sides', (arcChain, 'se'), (arcChain.getTransformedCopy(angle=120), 'es'))
		# , distance='parent.oneSide.endArc.endPoint*-1'
		topShape = ShapeGroup('top', sides)
		# for angle in range(0, 360, 30):
			# topShape.subShapes.append(holes.getTransformedCopy(angle = angle))
		self.shapes.append(topShape)
		Design.build(self)
class ThreeSidedThing(Design):
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
			'radius' :5
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		},{
			'angleSpan' : 60,
			'radius' : 5,
		},{
			'angleSpan' : 30,
			'radius' : 5,
		}])
		holes = HolesOnArcChain(arcChain, {
			'holeDistance' : 0.2, 
			'holeRadii' : [0.125, 0.5, 1, 0.125],
			'id' : 'holeChain'
		})
		endArc = Arc({
			'startPoint' : (0, 0),
			'startAngle' : 90,
			'endAngle' : 270,
			'radius' : 3,
			'reverse' : True,
			'id' : 'endArc'
		})
		circle = Circle({
			'centerPoint' : 'parent.arcChain.arc2.centerPoint',
			'radius' : 1
		})
		oneSide = ShapeGroup('oneSide', arcChain, endArc, circle)
		sideTwo = oneSide.getTransformedCopy(angle=120)
		sides = ShapeGroup('sides', oneSide, sideTwo)
		# , distance='parent.oneSide.endArc.endPoint*-1'
		topShape = ShapeGroup('top', sides)
		# for angle in range(0, 360, 30):
			# topShape.subShapes.append(holes.getTransformedCopy(angle = angle))
		self.shapes.append(topShape)
		Design.build(self)


class HoleySpiralArm(Design):
	def build(self):
		self.shapes = []
		spiral = Spiral({
			'startAngle' : 45, 
			'centerPoint' : (0,0), 
			'angleSpan' : 420, 
			'scaleFactor' : 0.5, 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'any.spiral.endPoint',
			'startAngle' : 'any.spiral.endAngle+180',
			'endAngle' : 'any.spiral.endAngle+250',
			'radius' : 4,
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'any.arc1.endPoint',
			'startAngle' : 'any.arc1.endAngle+180',
			'radius' : 5,
			'endAngle' : 'any.arc1.endAngle+100',
			'reverse' : True,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		middleCurve = ShapeGroup('middleCurve', spiral, arc1, arc2)

		spiral = Spiral({
			'startAngle' : 'any.middleCurve.spiral.startAngle', 
			'centerPoint' : (0,0), 
			'angleSpan' : 'any.middleCurve.spiral.angleSpan', 
			'scaleFactor' : 'any.middleCurve.spiral.scaleFactor*1.2', 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'any.spiral.endPoint',
			'startAngle' : 'any.spiral.endAngle+180',
			'endAngle' : 'any.spiral.endAngle+250',
			'radius' : 'any.middleCurve.arc1.radius*0.7',
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'any.arc1.endPoint',
			'startAngle' : 'any.arc1.endAngle+180',
			'radius' : 'any.middleCurve.arc2.radius*1.4',
			'endAngle' : 'any.arc1.endAngle+120',
			'reverse' : True,
			'id' : 'arc2',
			'changeableParams' : ['endAngle']
		})
		outerCurve = ShapeGroup('outerCurve', spiral, arc1, arc2)

		spiral = Spiral({
			'startAngle' : 'any.middleCurve.spiral.startAngle', 
			'centerPoint' : (0,0), 
			'angleSpan' : 'any.middleCurve.spiral.angleSpan+30', 
			'scaleFactor' : 'any.middleCurve.spiral.scaleFactor*0.8', 
			'growthFactorAdjustment' : 1, 
			'reverse' : True,
			'id' : 'spiral'
		})
		arc1 = Arc({
			'startPoint' : 'any.spiral.endPoint',
			'startAngle' : 'any.spiral.endAngle+180',
			'endAngle' : 'any.spiral.endAngle+250',
			'radius' : 'any.middleCurve.arc1.radius*1.2',
			'reverse' : False,
			'id' : 'arc1',
			'changeableParams' : []
		})
		arc2 = Arc({
			'startPoint' : 'any.arc1.endPoint',
			'startAngle' : 'any.arc1.endAngle+180',
			'radius' : 'any.middleCurve.arc2.radius*0.8',
			'endAngle' : 'any.arc1.endAngle+100',
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
		middleCurve.updateParam('dontRenderSubShapes', True)
		self.shapes.append(topShape)
		Design.build(self)
