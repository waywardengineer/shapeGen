from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from .shapeUtils import *
from .shapeBases import *
from .shapes import *

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
	scalableParams = ['traceWidth', 'knobRadius', 'socketRadius', 'socketWidth', 'segmentLength']
	pointParams = ['startPoint', 'endPoint']
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


