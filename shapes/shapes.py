from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *
from Spiral import Spiral

class ShapeGroup(Shape):
	def __init__(self, id, *shapes):
		Shape.__init__(self, {'id' : id})
		self.subShapes.extend([shape for shape in shapes])
		if self.p.id:
			for shape in self.subShapes:
				shape.setParent(self)


class Circle(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer)
		if not self.p.exclude:
			circle = dxf.circle(self.p.radius, self.p.centerPoint, layer=layer)
			drawing.add(circle)


class Line(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer)
		line = dxf.line(self.p.startPoint, self.p.endPoint, layer=layer)
		drawing.add(line)


class Arc(Shape):
	def calculate(self, *args): #takes [startPoint, startAngle, endPoint] or [startPoint, startAngle, radius, endAngle] or [centerPoint, radius, startAngle, endAngle]
		if listContains(['startPoint', 'startAngle', 'endPoint'], self.p.keys()):
			startPoint = self.p.startPoint
			startAngleRads = radians(self.p.startAngle)
			endPoint = self.p.endPoint
			rightTriangleCornerOffset = ((endPoint[0] - startPoint[0]) / 2., (endPoint[1] - startPoint[1]) / 2.)
			adjacentAngleRads = atan2(rightTriangleCornerOffset[1], rightTriangleCornerOffset[0])
			triangleAngleRads = startAngleRads - adjacentAngleRads
			radius = hypot(*rightTriangleCornerOffset) / abs(cos(triangleAngleRads))
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endAngleRads = atan2(endPoint[1] - centerPoint[1], endPoint[0] - centerPoint[0])
			centerEndDist = hypot(centerPoint[0] - endPoint[0], centerPoint[1] - endPoint[1])
			if not (radius * 0.95 < centerEndDist < 1.05 * radius):
				startAngleRads += pi
				triangleAngleRads = startAngleRads - adjacentAngleRads
				radius = hypot(*rightTriangleCornerOffset) / abs(cos(triangleAngleRads))
				centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
				endAngleRads = atan2(endPoint[1] - centerPoint[1], endPoint[0] - centerPoint[0])
				self.p.startAngle = self.p.startAngle + 180
			self.p.radius = radius
			self.p.centerPoint = centerPoint
			self.p.endAngle = degrees(endAngleRads)
		elif listContains(['startPoint', 'startAngle', 'radius', 'endAngle'], self.p.keys()):
			startPoint = self.p.startPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (startPoint[0] - radius * cos(startAngleRads), startPoint[1] - radius * sin(startAngleRads))
			endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
			self.p.centerPoint = centerPoint
			self.p.endPoint = endPoint
		elif listContains(['endPoint', 'startAngle', 'radius', 'endAngle'], self.p.keys()):
			endPoint = self.p.endPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			centerPoint = (endPoint[0] - radius * cos(endAngleRads), endPoint[1] - radius * sin(endAngleRads))
			startPoint = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.p.centerPoint = centerPoint
			self.p.startPoint = startPoint
		elif listContains(['centerPoint', 'radius', 'startAngle', 'endAngle'], self.p.keys()):
			centerPoint = self.p.centerPoint
			startAngleRads = radians(self.p.startAngle)
			endAngleRads = radians(self.p.endAngle)
			radius = self.p.radius
			self.p.startPoint = (centerPoint[0] + radius * cos(startAngleRads), centerPoint[1] + radius * sin(startAngleRads))
			self.p.endPoint = (centerPoint[0] + radius * cos(endAngleRads), centerPoint[1] + radius * sin(endAngleRads))
		else:
			print self.p
			raise Exception('No valid combination of arc data')
		if self.p.reverse:
			angleSpan = self.p.startAngle - self.p.endAngle
		else:
			angleSpan = self.p.endAngle - self.p.startAngle
		angleSpan = (angleSpan + 720) % 360
		self.p.angleSpan = angleSpan
		self.p.arcLength = self.p.radius * 2 * pi * angleSpan / 360.

	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer) 
		if not self.error:
			if self.p.reverse:
				arc = dxf.arc(self.p.radius, self.p.centerPoint, self.p.endAngle, self.p.startAngle, layer = '0')
			else:
				arc = dxf.arc(self.p.radius, self.p.centerPoint, self.p.startAngle, self.p.endAngle, layer = '0')
			drawing.add(arc)


class BezCurve(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing) #params: {'points' : [((x, y), angle, (strengthIn, strengthOut))]}
		curve = dxf.bezier(layer = layer)
		points = self.p['points']
		vectors = self.makeVectors(self.p['points'][0])
		curve.start(points[0][0], vectors[1])
		for i in range(1, len(points)):
			strengthIn = points[i][2][0]
			strengthOut = points[i][2][1]
			angle = radians(points[i][1])
			vectors = self.makeVectors(self.p['points'][i])
			segments = int(hypot(points[i-1][0][0] - points[i][0][0], points[i-1][0][1] - points[i][0][1]) / minLineSize) + 1
			curve.append(points[i][0], vectors[0], vectors[1], segments)
		drawing.add(curve)

	def makeVectors(self, point):
		angle = radians(point[1])
		unitVectorOut = (cos(angle), sin(angle))
		unitVectorIn = (-unitVectorOut[0], -unitVectorOut[1])
		strengthIn = point[2][0]
		strengthOut = point[2][1]
		vectorOut = (unitVectorOut[0] * strengthOut, unitVectorOut[1] * strengthOut)
		vectorIn = (unitVectorIn[0] * strengthIn, unitVectorIn[1] * strengthIn)
		return (vectorIn, vectorOut)

	def applyTransforms(self):
		transforms = deepcopy(self.transforms)
		Shape.applyTransforms(self)
		for transform in transforms:
			(angle, distance) = transform
			newPoints = []
			for point in self.p['points']:
				newPoint = (
					transformPoint(point[0], angle, distance),
					point[1] + angle,
					point[2]
				)
				newPoints.append(newPoint)
			self.p['points'] = newPoints


class ArcChain(ShapeGroup):
	def __init__(self, id, definitions):
		ShapeGroup.__init__(self,id)
		for i, definition in enumerate(definitions):
			if 'growthFactorAdjustment' in definition.keys():
				shape = Spiral(definition)
			else:
				shape = Arc(definition)
			self.addSubShape(shape)
			shape.updateParam('id', 'arc' + str(i))
			if i > 0:
				lastShape = self.subShapes[i-1]
				if shape.p.noDirectionAlternate:
					reverse = lastShape.p.reverse
				else:
					reverse = not lastShape.p.reverse
				shape.updateParam('reverse', reverse)
				if shape.p.type == 'Arc':
					if shape.p.noDirectionAlternate:
						angleChangeStr = ''
					else:
						angleChangeStr = ' + 180'
					shape.updateParam('startPoint', '.'.join([lastShape.p.id, 'endPoint']))
					shape.updateParam('startAngle', '.'.join([lastShape.p.id, 'endAngle' + angleChangeStr]))
			if shape.p.type == 'Arc' and shape.p.angleSpan:
				if shape.p.reverse:
					endAngleStr = 'startAngle - ' + str(shape.p.angleSpan)
				else:
					endAngleStr = 'startAngle + ' + str(shape.p.angleSpan)
				shape.updateParam('endAngle', endAngleStr)

	def calculate(self):
		self.p.startPoint = self.subShapes[0].p.startPoint
		self.p.startAngle = self.subShapes[0].p.startAngle
		self.p.endPoint = self.subShapes[-1].p.endPoint
		self.p.endAngle = self.subShapes[-1].p.endAngle

class ShapeChain(ShapeGroup):
	def __init__(self, id, *shapesAndConnections):
		ShapeGroup.__init__(self, id, *[s[0] for s in shapesAndConnections])
		self.connections = [s[1] for s in shapesAndConnections]

	def calculate(self):
		pointNames = {'e' : 'endPoint', 's' : 'startPoint'}
		for i in range(1, len(self.connections)):
			fromPointName = pointNames[self.connections[i-1][1]]
			toPointName = pointNames[self.connections[i][0]]
			fromShape = self.subShapes[i-1]
			toShape = self.subShapes[i]
			transform = (
				getattr(fromShape.p, fromPointName)[0] - getattr(toShape.p, toPointName)[0],
				getattr(fromShape.p, fromPointName)[1] - getattr(toShape.p, toPointName)[1]
			)
			toShape.transform(distance=transform)
			toShape.applyTransforms()
		chainStartPointName = pointNames[self.connections[0][0]]
		chainEndPointName = pointNames[self.connections[-1][1]]
		self.p.startPoint = getattr(self.subShapes[0].p, chainStartPointName)
		self.p.endPoint = getattr(self.subShapes[-1].p, chainEndPointName)

class OffsetArcChain(ArcChain):
	def __init__(self, arcChain, params):
		Shape.__init__(self, params)
		self.arcChain = arcChain
		previousArc = False
		cumulativeAngleOffset = 0
		for i, arc in enumerate(arcChain.subShapes):
			if arc.p.reverse:
				operation = '-'
			else:
				operation = '+'
			cumulativeAngleOffset += self.p.angleOffset
			radius = ' '.join(['.'.join([arcChain.p.id, arc.p.id, 'radius']), operation, str(self.p.offset)])
			endAngle = ' '.join(['.'.join([arcChain.p.id, arc.p.id, 'endAngle']), operation, str(cumulativeAngleOffset)])
			reverse = arc.p.reverse
			id = 'arc' + str(i)
			if not previousArc:
				self.addSubShape(Arc({
					'id' : id,
					'centerPoint' : '.'.join([arcChain.p.id, arc.p.id, 'centerPoint']),
					'radius' : radius,
					'startAngle' : '.'.join([arcChain.p.id, arc.p.id, 'startAngle']),
					'endAngle' : endAngle,
					'reverse' : reverse
				}))
			else:
				startAngle = '.'.join([previousArc.p.id, 'endAngle'])
				if not previousArc.p.reverse == arc.p.reverse:
					startAngle += ' + 180'
				self.addSubShape(Arc({
					'id' : id,
					'startPoint' : '.'.join([previousArc.p.id, 'endPoint']),
					'radius' : radius,
					'startAngle' : startAngle,
					'endAngle' : endAngle,
					'reverse' : reverse
				}))
			previousArc = arc


