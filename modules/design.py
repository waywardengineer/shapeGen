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
			shape.build(shape)
			
	def updateValue(self, id, value):
		self.modifiedParams[id] = value

class TestDesign(Design):
	def build(self):
		self.shapes = []
		inner = ArcChain('inner', [{
			'sweepStartAngle' : 30,
			'centerPoint' : (0, 0),
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 1,
			'sweepAngleSpan' : 330,
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :5,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		}])
		circle = Circle({
			'id' : 'tube',
			'centerPoint' : (0,0),
			'radius' : 1.5
		})
		outer = ArcChain('outer', [{
			'sweepStartAngle' : 'inner.arc0.sweepStartAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 1.1,
			'sweepAngleSpan' : 'inner.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :5,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,#center
			'radius' : 3
		}])
		circle = Circle({
			'id' : 'tube',
			'centerPoint' : (0,0),
			'radius' : 1.5
		})
		# holes = HolesOnArcChain(arcChain, {
			# 'holeDistance' : 0.2, 
			# 'holeRadii' : [0.125, 0.5, 1, 0.125],
		# })
		# arc1 = Arc({
			# 'startPoint' : (0, 0),
			# 'startAngle' : 90,
			# 'endAngle' : 'startAngle+90',
			# 'radius' : 3,
			# 'reverse' : True,
			# 'id' : 'arc1'
		# })
		# arc2 = Arc({
			# 'startPoint' : 'arc1.endPoint+arc1.startPoint',
			# 'startAngle' : 'arc1.endAngle+90',
			# 'endAngle' : 270,
			# 'radius' : 3,
			# 'reverse' : True,
			# 'id' : 'arc2'
		# })
		# arc3 = Arc({
			# 'startPoint' : 'arc2.endPoint',
			# 'startAngle' : 'arc2.endAngle+90',
			# 'endAngle' : 270,
			# 'radius' : 3,
			# 'reverse' : True,
			# 'id' : 'arc'
		# })
		group = ShapeGroup('group', inner, outer)
		# group.transform(angle='arc2.startAngle')
		# circle = Circle({
			# 'centerPoint' : 'parent.arcChain.arc2.centerPoint',
			# 'radius' : 1
		# })
		# oneSide = ShapeChain('oneSide', (endArc, 'es'), (arcChain, 'se'))
		# sides = ShapeChain('sides', (oneSide, 'es'), (oneSide.getTransformedCopy(angle=120), 'es'), (oneSide.getTransformedCopy(angle=240), 'es'))
		# spiral = Spiral({
			# 'sweepStartAngle' : 45, 
			# 'centerPoint' : (0,0), 
			# 'sweepAngleSpan' : 420, 
			# 'scaleFactor' : 0.5, 
			# 'growthFactorAdjustment' : 1, 
			# 'reverse' : True,
			# 'id' : 'spiral'
		# })
		# holes = HolesOnArcChain(arcChain, {
			# 'holeDistance' : 0.125, 
			# 'holeRadii' : [0.125, 0.25, 1, 0.5],
			# 'id' : 'holeChain',
			# 'changeableParams' : ['holeDistance']
		# })
		topShape = ShapeGroup('top', group)
		# for angle in range(0, 360, 30):
			# topShape.subShapes.append(holes.getTransformedCopy(angle = angle))
		self.shapes.append(topShape)
		Design.build(self)
		
class NewDesign(Design):
	def build(self):
		self.shapes = []
		inner = ArcChain('inner', [{
			'sweepStartAngle' : 30,
			'centerPoint' : (0, 0),
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 1,
			'sweepAngleSpan' : 330,
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :5,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,#center
			'radius' : 6
		}])
		circle = Circle({
			'id' : 'tube',
			'centerPoint' : (0,0),
			'radius' : 1.5
		})
		outer = ArcChain('outer', [{
			'sweepStartAngle' : 'inner.arc0.sweepStartAngle',
			'centerPoint' : (0, 0),
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 1.2,
			'sweepAngleSpan' : 'inner.arc0.sweepAngleSpan',
			'reverse' : True
		},{
			'angleSpan' : 60,
			'radius' :4,
		}])
		side = ShapeGroup('side', inner, outer)
		side.p.startPoint = 'outer.endPoint'
		side.p.endPoint = 'inner.endPoint'
		side2 = side.getTransformedCopy(angle = 120)
		side3 = side.getTransformedCopy(angle = 240)
		sides = ShapeChain('sides', (side, 'se'), (side2, 'se'), (side3, 'se'))
		circle = Circle({
			'centerPoint' : 'avgPoints ( side.inner.arc2.centerPoint , side1.inner.arc2.centerPoint , side2.inner.arc2.centerPoint )',
			'radius' : 5
		})
		topShape = ShapeGroup('top', sides, circle)
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
			'startAngle' : 'oneEdge.arcChain.arc2.startAngle+5', 
			'endAngle' : 'oneEdge.arcChain.arc2.endAngle-5', 
			'centerPoint' : 'oneEdge.arcChain.arc2.centerPoint',
			'radius' : 'oneEdge.arcChain.arc2.radius-0.75',
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
			'sweepStartAngle' : 45, 
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
		sides.s.b.s.b.updateParam('radius', 'oneSide.circle.radius*1.2')
		sides.s.c.s.b.updateParam('radius', 'oneSide.circle.radius*1.5')
		# for angle in range(0, 360, 30):
			# topShape.subShapes.append(holes.getTransformedCopy(angle = angle))
		self.shapes.append(topShape)
		Design.build(self)


class HoleySpiralArm(Design):
	def build(self):
		self.shapes = []
		spiral = Spiral({
			'sweepStartAngle' : 45, 
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
			'sweepStartAngle' : 'middleCurve.spiral.sweepStartAngle', 
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
			'sweepStartAngle' : 'middleCurve.spiral.sweepStartAngle', 
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
		middleCurve.updateParam('dontRenderSubShapes', True)
		self.shapes.append(topShape)
		Design.build(self)
