from .DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class AlienSpineCircuitTraces(Design):
	def build(self):
		self.shapes = []
		traces = NodeyCircuitTraceGroup({
			'points' : [(0, 0), (0, 10), (5, 15), (5, 20), (10, 25)],
			'numTraces' : 5,
		})
		traces2 = NodeyCircuitTraceGroup({
			'points' : [(-3.75, 0), (-3.75, 20), (-15, 20), (-15, 30)],
			'numTraces' : 5,
		})
		spine = SpineyCircuitTraceGroup({
			'vectors' : [(15, 0), (0, 20), getEndPoint((0, 0), 60, endY=10), (0, 15), getEndPoint((0, 0), 120, endY=10), getEndPoint((0, 0), 121, endY=18)],
			'id' : 'spine',
			'numTraces' : 1,
			'segmentLength' : 20,
		})
		spine.calculate()
		topShape = ShapeGroup('top', spine)
		numPoints = len(spine.p.attachmentPoints[0])
		oldAngle = False
		segmentIndex = -1
		directions = [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]
		line1Lengths = [(5, 3), (4, 2.5), (1.5, 4), (1.5, 4), (6, 4)]
		line2Lengths = [(17, 23), (9, 14), (14, 10), (10, 10), (18, 10)]
		line2Angles = [(0, 30), (30, 0), (30, 0), (30, 30), (0, 30)]
		groupEndPoints = [[], []]
		traceCounts = [[], []]
		traceEndPoints = [[], []]
		for i in range(numPoints):
			spineAngle = spine.p.attachmentPoints[0][i][1] - 60
			if not spineAngle == oldAngle:
				segmentCount = 0
				segmentIndex += 1
				oldAngle = spineAngle
				startLinePos = transformPoint(spine.p.attachmentPoints[0][i][0], - (spineAngle - 90))[1]
				for j in range(2):
					if traceEndPoints[j]:
						groupEndPoints[j].append(avgPoints(*traceEndPoints[j]))
						traceCounts[j].append(len(traceEndPoints[j]))
					traceEndPoints[j] = []
				firstLineEndPoints = [[False, False], [False, False]]
			for j in range(2):
				if j == 0:
					line1Angle = spineAngle + 60
					line2Angle = spineAngle + line2Angles[segmentIndex][j]
				else:
					line1Angle = spineAngle - 60
					line2Angle = spineAngle - line2Angles[segmentIndex][j]
				if directions[segmentIndex][j]:
					if not firstLineEndPoints[j][0]:
						vector = transformPoint((line1Lengths[segmentIndex][j], 0), line1Angle)
						line1EndPoint = addVectors(spine.p.attachmentPoints[j][i][0], vector)
						vector = transformPoint((line2Lengths[segmentIndex][j], 0), line2Angle)
						line2EndPoint = addVectors(line1EndPoint, vector)
						firstLineEndPoints[j] = [line1EndPoint, line2EndPoint]
					else:
						offsetVector = transformPoint((0.75 * (directions[segmentIndex][j] * segmentCount), 0), line2Angle + 90 - 180 * j)
						point = addVectors(offsetVector, firstLineEndPoints[j][0])
						line1EndPoint = getIntersect(point, line2Angle, spine.p.attachmentPoints[j][i][0], line1Angle)
						line2EndPoint = addVectors(firstLineEndPoints[j][1], offsetVector)
					topShape.addSubShape(NodeyCircuitTrace({
						'startPoint' : spine.p.attachmentPoints[j][i][0],
						'endPoint' : line1EndPoint,
					}))
					topShape.addSubShape(NodeyCircuitTrace({
						'startPoint' : line1EndPoint,
						'endPoint' : line2EndPoint
					}))
					traceEndPoints[j].append(line2EndPoint)
			segmentCount += 1
		for j in range(2):
			if traceEndPoints[j]:
				groupEndPoints[j].append(avgPoints(*traceEndPoints[j]))
				traceCounts[j].append(len(traceEndPoints[j]))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][0], (0, 5), getEndPoint((0, 0), 120, endY=10), getEndPoint((0, 0), 150, endY=10)],
			'numTraces' : traceCounts[0][0],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][1], getEndPoint((0, 0), 90, endY=2), getEndPoint((0, 0), 120, endY=5), getEndPoint((0, 0), 150, endY=10)],
			'numTraces' : traceCounts[0][1],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][2], getEndPoint((0, 0), 120, endY=2), getEndPoint((0, 0), 150, endY=10)],
			'numTraces' : traceCounts[0][2],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][3], getEndPoint((0, 0), 150, endY=10)],
			'numTraces' : traceCounts[0][3],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[1][0], getEndPoint((0, 0), 60, endY=2), (0, 40), getEndPoint((0, 0), 60, endY=6)],
			'numTraces' : traceCounts[1][0],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[1][1], getEndPoint((0, 0), 60, endY=2), (0, 31), getEndPoint((0, 0), 60, endY=6)],
			'numTraces' : traceCounts[1][1],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[1][2], (0, 1.5), getEndPoint((0, 0), 60, endY=2), (0, 31), getEndPoint((0, 0), 60, endY=6)],
			'numTraces' : traceCounts[1][2],
		}))
		topShape.addSubShape(Line({'startPoint' : (0, 0), 'endPoint' : (33, 0)}))
		topShape.addSubShape(Line({'startPoint' : (33, 0), 'endPoint' : (33, 70)}))
		topShape.addSubShape(Line({'startPoint' : (33, 70), 'endPoint' : (0, 70)}))
		topShape.addSubShape(Line({'startPoint' : (0, 70), 'endPoint' : (0, 0)}))
		self.shapes.append(topShape)
		Design.build(self)
