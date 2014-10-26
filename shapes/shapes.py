from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin, tan
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *


class ShapeGroup(Shape):
	def __init__(self, id, *shapes):
		Shape.__init__(self, {'id' : id})
		self.subShapes.extend([shape for shape in shapes])
		if self.p.id:
			for shape in self.subShapes:
				shape.setParent(self)
	def calculate(self):
		Shape.calculate(self)

class Circle(Shape):
	def addToDrawing(self, drawing, layer='0'):
		Shape.addToDrawing(self, drawing, layer)
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
		indexForPrepends = 0
		for i, definition in enumerate(definitions):
			if 'growthFactorAdjustment' in definition.keys():
				shape = Spiral(definition)
			else:
				shape = Arc(definition)
			self.addSubShape(shape)
			shape.updateParam('id', 'arc' + str(i))
			if i > 0:
				if shape.p.prepend:
					lastShape = self.subShapes[indexForPrepends]
					indexForPrepends = i
				else:
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
					if shape.p.prepend:
						shape.updateParam('endPoint', '.'.join([lastShape.p.id, 'startPoint']))
						shape.updateParam('endAngle', '.'.join([lastShape.p.id, 'startAngle' + angleChangeStr]))
					else:
						shape.updateParam('startPoint', '.'.join([lastShape.p.id, 'endPoint']))
						shape.updateParam('startAngle', '.'.join([lastShape.p.id, 'endAngle' + angleChangeStr]))
			if shape.p.type == 'Arc' and shape.p.angleSpan:
				if shape.p.prepend:
					if shape.p.reverse:
						startAngleStr = 'endAngle + ' + str(shape.p.angleSpan)
					else:
						startAngleStr = 'endAngle - ' + str(shape.p.angleSpan)
					shape.updateParam('startAngle', startAngleStr)
				else:
					if shape.p.reverse:
						endAngleStr = 'startAngle - ' + str(shape.p.angleSpan)
					else:
						endAngleStr = 'startAngle + ' + str(shape.p.angleSpan)
					shape.updateParam('endAngle', endAngleStr)

	def calculate(self):
		newSubShapes =  []
		for shape in self.subShapes:
			if shape.p.prepend:
				newSubShapes = [shape] + newSubShapes
			else:
				newSubShapes.append(shape)
		self.subShapes = newSubShapes
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
			toShape.transforms.resolve()
			toShape.applyResolvedTransforms()
		chainStartPointName = pointNames[self.connections[0][0]]
		chainEndPointName = pointNames[self.connections[-1][1]]
		self.p.startPoint = getattr(self.subShapes[0].p, chainStartPointName)
		self.p.endPoint = getattr(self.subShapes[-1].p, chainEndPointName)

class CurvyCircuitTrace(Shape):
	def calculate(self):
		self.angles = []
		for i in range(len(self.p.points)-1):
			firstPoint = self.p.points[i]
			secondPoint = self.p.points[i + 1]
			angleInRads = atan2(secondPoint[1] - firstPoint[1], secondPoint[0] - firstPoint[0])
			self.angles.append(angleInRads)
		totalWidth = self.p.numTraces * self.p.traceWidth + (self.p.numTraces - 1) * self.p.traceSpacing
		for i in range(self.p.numTraces):
			offset = (-0.5 * totalWidth) + i * (self.p.traceWidth + self.p.traceSpacing)
			self.makeSingleLine(offset)
			offset += self.p.traceWidth
			self.makeSingleLine(offset)

	def makeSingleLine(self, offset):
		points = []
		angle = self.angles[0]
		vector = (offset * sin(angle), offset * cos(angle))
		points.append(addVectors(self.p.points[0], vector))
		lastEndPoint = points[0]
		for i in range(len(self.angles)-1):
			angle = (self.angles[i] - pi/2) - (self.angles[i] - self.angles[i+1]) / 2
			distFactor = 1 / cos((self.angles[i] - self.angles[i+1]) / 2)
			dist = offset * distFactor
			vector = (dist * cos(angle), dist * sin(angle))
			points.append(addVectors(self.p.points[i+1], vector))
		angle = self.angles[-1]
		vector = (offset * sin(angle), offset * cos(angle))
		points.append(addVectors(self.p.points[-1], vector))
		for i in range(len(self.angles)-1):
			angle = (self.angles[i] - pi/2) - (self.angles[i] - self.angles[i+1]) / 2
			reverse = self.angles[i] > self.angles[i+1]
			distFactor = 1 / cos((self.angles[i] - self.angles[i+1]) / 2)
			if reverse:
				correction = 450
				radius = self.p.radius - offset
			else:
				correction = 270
				distFactor = - distFactor
				radius = self.p.radius + offset
			if radius < 0:
				radius = 0
			dist = radius * distFactor
			vector = (dist * cos(angle), dist * sin(angle))
			centerPoint = addVectors(points[i+1], vector)
			arc = Arc({
				'centerPoint' : centerPoint,
				'reverse' : reverse,
				'startAngle' : (degrees(self.angles[i]) + correction) % 360,
				'endAngle' : (degrees(self.angles[i+1]) + correction) % 360,
				'radius' : radius
			})
			self.addSubShape(arc)
			arc.calculate()
			self.addSubShape(Line({
				'startPoint' : lastEndPoint,
				'endPoint' : arc.p.startPoint
			}))
			lastEndPoint = arc.p.endPoint
		self.addSubShape(Line({
			'startPoint' : lastEndPoint,
			'endPoint' : points[-1]
		}))
class NodeyCircuitTrace(Shape):
	defaultParams = {
		'traceWidth' : 0.2,
		'knobRadius' : [0.15, 0.3],
		'socketRadius' : [0.25, 0.35],
		'socketWidth' : [0.49, 0.65],
		'endFlareAngle' : 15,
		'segmentLength' : 10,
		'nodeSizes' : [1, 1]
	}
	def calculate(self):
		lineAngle = atan2(self.p.endPoint[1] - self.p.startPoint[1], self.p.endPoint[0] - self.p.startPoint[0])
		triangleAngle = asin(self.p.traceWidth / (2 * self.p.knobRadius[self.p.nodeSizes[1]]))
		startAngle = lineAngle + pi + triangleAngle
		endAngle = lineAngle + pi - triangleAngle
		arc = Arc({
			'centerPoint' : self.p.endPoint,
			'radius' : self.p.knobRadius[self.p.nodeSizes[1]],
			'startAngle' : degrees(startAngle),
			'endAngle' : degrees(endAngle)
		})
		arc.calculate()
		trPoint = arc.p.startPoint
		tlPoint = arc.p.endPoint
		self.addSubShape(arc)
		triangleAngle = asin(self.p.socketWidth[self.p.nodeSizes[0]] / (2 * self.p.socketRadius[self.p.nodeSizes[0]]))
		startAngle = lineAngle - triangleAngle
		endAngle = lineAngle + triangleAngle
		arc = Arc({
			'centerPoint' : self.p.startPoint,
			'radius' : self.p.socketRadius[self.p.nodeSizes[0]],
			'startAngle' : degrees(startAngle),
			'endAngle' : degrees(endAngle)
		})
		arc.calculate()
		brPoint = arc.p.startPoint
		blPoint = arc.p.endPoint
		self.addSubShape(arc)
		lineEndDist = (self.p.socketWidth[self.p.nodeSizes[0]] - self.p.traceWidth) / (2 * tan(radians(self.p.endFlareAngle)))
		vector = transformPoint((lineEndDist, - (self.p.socketWidth[self.p.nodeSizes[0]] - self.p.traceWidth) / 2), degrees(lineAngle))
		m2lPoint = addVectors(blPoint, vector)
		m1lPoint = addVectors(blPoint, (vector[0] / 2, vector[1] / 2))
		vector = transformPoint((lineEndDist, (self.p.socketWidth[self.p.nodeSizes[0]] - self.p.traceWidth) / 2), degrees(lineAngle))
		m2rPoint = addVectors(brPoint, vector)
		m1rPoint = addVectors(brPoint, (vector[0] / 2, vector[1] / 2))
		arc = Arc({
			'startPoint' : blPoint,
			'endPoint' : m1lPoint,
			'startAngle' : degrees(lineAngle) + 90,
			'reverse' : True
		})
		arc.calculate()
		self.addSubShape(arc)
		arc = Arc({
			'startPoint' : m2lPoint,
			'endPoint' : m1lPoint,
			'startAngle' : degrees(lineAngle) - 90,
			'reverse' : True
		})
		arc.calculate()
		self.addSubShape(arc)
		arc = Arc({
			'startPoint' : brPoint,
			'endPoint' : m1rPoint,
			'startAngle' : degrees(lineAngle) + 90,
			'reverse' : False
		})
		arc.calculate()
		self.addSubShape(arc)
		arc = Arc({
			'startPoint' : m2rPoint,
			'endPoint' : m1rPoint,
			'startAngle' : degrees(lineAngle) - 90,
			'reverse' : False
		})
		arc.calculate()
		self.addSubShape(arc)
		if self.p.type == 'NodeyCircuitTrace':
			self.addSubShape(Line({'startPoint' : trPoint, 'endPoint' : m2rPoint}))
			self.addSubShape(Line({'startPoint' : tlPoint, 'endPoint' : m2lPoint}))
		return (lineAngle, trPoint, tlPoint, m2rPoint, m2lPoint)


class NodeyCircuitTraceGroup(Shape):
	defaultParams = {
		'traceClass' : 'NodeyCircuitTrace',
		'traceSpacing' : 0.75,
		'segmentLength' : 5
	}
	traceClass = NodeyCircuitTrace
	def __init__(self, *args, **kwargs):
		Shape.__init__(self, *args, **kwargs)
		if self.p.vectors:
			points = [self.p.vectors[0]]
			for vector in self.p.vectors[1:]:
				newPoint = addVectors(points[-1], vector)
				points.append(newPoint)
			self.p.points = points
		mainLines = []
		self.lineAngles = []
		self.angleIndices = []
		segmentCounts = []
		for i in range(len(self.p.points)-1):
			vector = (self.p.points[i + 1][0] - self.p.points[i][0], self.p.points[i + 1][1] - self.p.points[i][1])
			segmentCounts.append(1 + int(hypot(*vector) / self.p.segmentLength))
			angleInRads = atan2(vector[1], vector[0])
			self.lineAngles.append(angleInRads)
		for i in range(self.p.numTraces):
			offset = (-0.5 * (self.p.numTraces - 1) * self.p.traceSpacing) + i * (self.p.traceSpacing)
			vector = transformPoint((0, -offset), degrees(self.lineAngles[0]))
			line = [addVectors(self.p.points[0], vector)]
			for j in range(len(self.lineAngles) - 1):
				angle = (self.lineAngles[j] - pi/2) - (self.lineAngles[j] - self.lineAngles[j+1]) / 2
				distFactor = 1 / cos((self.lineAngles[j] - self.lineAngles[j+1]) / 2)
				dist = offset * distFactor
				vector = (dist * cos(angle), dist * sin(angle))
				line.append(addVectors(self.p.points[j+1], vector))
			vector = transformPoint((0, -offset), degrees(self.lineAngles[-1]))
			line.append(addVectors(self.p.points[-1], vector))
			mainLines.append(line)
		lines = []
		nodeSizes = []
		for line in mainLines:
			newLine = []
			nodeSizeList = []
			for i in range(len(line) - 1):
				vector = (line[i + 1][0] - line[i][0], line[i + 1][1] - line[i][1])
				numSegments = segmentCounts[i]
				nodeSize = 1
				for j in range(numSegments):
					newLine.append(addVectors(line[i], (vector[0] * (float(j) / numSegments), vector[1] * (float(j) / numSegments))))
					nodeSizeList.append(nodeSize)
					nodeSize = 0
			nodeSizeList.append(1)
			nodeSizes.append(nodeSizeList)
			newLine.append(line[-1])
			lines.append(newLine)
		for j in range(len(lines)):
			line = lines[j]
			for i in range(len(line) - 1):
				trace = self.traceClass({
					'startPoint' : line[i],
					'endPoint' : line[i + 1],
					'nodeSizes' : [nodeSizes[j][i], nodeSizes[j][i + 1]]
				})
				self.addSubShape(trace)
				
class SpineyCircuitTrace(NodeyCircuitTrace):
	defaultParams = {
		'traceWidth' : 1,
		'knobRadius' : [0.55, 0.75, 0.3],
		'socketRadius' : [0.65, 0.8],
		'socketWidth' : [1.25, 1.5],
		'endFlareAngle' : 15,
		'nodeSizes' : [1, 1],
		'spineAngle' : 60,
		'spineRadius' : 2,
		'spineSpacing' : 5
	}
	def calculate(self):
		(lineAngle, trPoint, tlPoint, m2rPoint, m2lPoint) = NodeyCircuitTrace.calculate(self)
		def makeSpineExtension(startPoint, reverse):
			if reverse:
				startAngle = degrees(lineAngle) + 90
				endAngle = startAngle - self.p.spineAngle - 5
			else:
				startAngle = degrees(lineAngle) - 90
				endAngle = startAngle + self.p.spineAngle + 5
			arc = Arc({
				'startPoint' : startPoint,
				'startAngle' : startAngle,
				'endAngle' : endAngle,
				'radius' : self.p.spineRadius,
				'reverse' : reverse
			})
			arc.calculate()
			self.addSubShape(arc)
			if reverse:
				startAngle2 = endAngle + 180
				endAngle2 = startAngle2 - 190
			else:
				startAngle2 = endAngle + 180
				endAngle2 = startAngle2 + 190
			arc = Arc({
				'startPoint' : arc.p.endPoint,
				'startAngle' : startAngle2,
				'endAngle' : endAngle2,
				'radius' : self.p.knobRadius[2],
				'reverse' : not reverse
			})
			arc.calculate()
			self.addSubShape(arc)
			centerPoint = arc.p.centerPoint
			arc = Arc({
				'startPoint' : arc.p.endPoint,
				'startAngle' : endAngle + 180,
				'endAngle' : startAngle,
				'radius' : 0.35 * self.p.spineRadius,
				'reverse' : reverse
			})
			arc.calculate()
			self.addSubShape(arc)
			return (arc.p.endPoint, centerPoint)
		lengthVector = (trPoint[0] - m2rPoint[0], trPoint[1] - m2rPoint[1])
		numSegments = 1 + int(hypot(*lengthVector) / self.p.spineSpacing)
		lAttachmentPoints = []
		rAttachmentPoints = []
		for i in range(numSegments):
			lStartPoint = addVectors(m2lPoint, (lengthVector[0] * float(i) / numSegments, lengthVector[1] * float(i) / numSegments)) 
			rStartPoint = addVectors(m2rPoint, (lengthVector[0] * float(i) / numSegments, lengthVector[1] * float(i) / numSegments)) 
			(lPoint, lCenterPoint) = makeSpineExtension(lStartPoint, False)
			(rPoint, rCenterPoint) = makeSpineExtension(rStartPoint, True)
			lAttachmentPoints.append([lCenterPoint, degrees(lineAngle) + self.p.spineAngle])
			rAttachmentPoints.append([rCenterPoint, degrees(lineAngle) - self.p.spineAngle])
			lEndPoint = addVectors(m2lPoint, (lengthVector[0] * float(i+1) / numSegments, lengthVector[1] * float(i+1) / numSegments)) 
			rEndPoint = addVectors(m2rPoint, (lengthVector[0] * float(i+1) / numSegments, lengthVector[1] * float(i+1) / numSegments)) 
			self.addSubShape(Line({'startPoint' : lPoint, 'endPoint' : lEndPoint}))
			self.addSubShape(Line({'startPoint' : rPoint, 'endPoint' : rEndPoint}))
		self.p.attachmentPoints = [lAttachmentPoints, rAttachmentPoints]

class SpineyCircuitTraceGroup(NodeyCircuitTraceGroup):
	traceClass = SpineyCircuitTrace
	def calculate(self):
		NodeyCircuitTraceGroup.calculate(self)
		attachmentPoints = [[], []]
		for trace in self.subShapes:
			trace.calculate()
			attachmentPoints[0] += trace.p.attachmentPoints[0]
			attachmentPoints[1] += trace.p.attachmentPoints[1]
		self.p.attachmentPoints = attachmentPoints

			