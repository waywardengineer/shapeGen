from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class TestDesign(Design):
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
			'vectors' : [(15, 0), (0, 20), getEndPoint((0, 0), 60, endY=10), (0, 15), getEndPoint((0, 0), 120, endY=18), getEndPoint((0, 0), 150, endY=18)],
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
		offsets = [(5, 15), (11, 2), (2.5, 4), (2.5, 4), (2.5, 4)]
		lengths = [(17, 30), (16, 15), (10, 10), (10, 10), (10, 10)]
		angles = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
		groupEndPoints = [[], []]
		traceCounts = [[], []]
		traceEndPoints = [[], []]
		for i in range(numPoints):
			lineAngle = spine.p.attachmentPoints[0][i][1] - 60
			if not lineAngle == oldAngle:
				segmentCount = 0
				segmentIndex += 1
				oldAngle = lineAngle
				startLinePos = transformPoint(spine.p.attachmentPoints[0][i][0], - (lineAngle - 90))[1]
				for j in range(2):
					if traceEndPoints[j]:
						groupEndPoints[j].append(avgPoints(*traceEndPoints[j]))
						traceCounts[j].append(len(traceEndPoints[j]))
					traceEndPoints[j] = []
			for j in range(2):
				xDist = offsets[segmentIndex][j] + 0.75 * (directions[segmentIndex][j] * segmentCount)
				yDist = xDist / tan(radians(60))
				if j == 0:
					xDist = - xDist
				vector = transformPoint((xDist, yDist), lineAngle - 90 + angles[segmentIndex][j])
				endPoint = addVectors(spine.p.attachmentPoints[j][i][0], vector)
				topShape.addSubShape(NodeyCircuitTrace({
					'startPoint' : spine.p.attachmentPoints[j][i][0],
					'endPoint' : endPoint,
				}))
				lineDist = startLinePos - transformPoint(endPoint, - (lineAngle - 90))[1]
				startPoint = endPoint
				endPoint = addVectors(endPoint, transformPoint((0, -(directions[segmentIndex][j] * lengths[segmentIndex][j]) + lineDist), (lineAngle-90)))
				traceEndPoints[j].append(endPoint)
				topShape.addSubShape(NodeyCircuitTrace({
					'startPoint' : startPoint,
					'endPoint' : endPoint
				}))
			segmentCount += 1
		for j in range(2):
			if traceEndPoints[j]:
				groupEndPoints[j].append(avgPoints(*traceEndPoints[j]))
				traceCounts[j].append(len(traceEndPoints[j]))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][0], (0, 5), getEndPoint((0, 0), 120, endY=10)],
			'numTraces' : traceCounts[0][0],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][1], getEndPoint((0, 0), 60, endY=2), getEndPoint((0, 0), 120, endY=10)],
			'numTraces' : traceCounts[0][1],
		}))
		topShape.addSubShape(NodeyCircuitTraceGroup({
			'vectors' : [groupEndPoints[0][2], (0, 2), getEndPoint((0, 0), 120, endY=10)],
			'numTraces' : traceCounts[0][2],
		}))
		topShape.addSubShape(Line({'startPoint' : (0, 0), 'endPoint' : (33, 0)}))
		topShape.addSubShape(Line({'startPoint' : (33, 0), 'endPoint' : (33, 70)}))
		topShape.addSubShape(Line({'startPoint' : (33, 70), 'endPoint' : (0, 70)}))
		topShape.addSubShape(Line({'startPoint' : (0, 70), 'endPoint' : (0, 0)}))
		self.shapes.append(topShape)
		Design.build(self)
		
		
		
			# tlArc = Arc({
				# 'startPoint' : 'outerSpiral.startPoint',
				# 'startAngle' : 'outerSpiral.startAngle + 180',
				# 'radius' : 0.03 * i,
				# 'endAngle' : 'startAngle + 40',
				# 'id' : 'tlArc'
			# })
			# blArc = Arc({
				# 'startPoint' : 'innerSpiral.startPoint',
				# 'startAngle' : 'innerSpiral.startAngle',
				# 'radius' : 0.02 * i,
				# 'endAngle' : 'startAngle - 70',
				# 'id' : 'blArc',
				# 'reverse' : True
			# })
			# lArc = Arc({
				# 'startPoint' : 'tlArc.endPoint',
				# 'startAngle' : 'tlArc.endAngle',
				# 'reverse' : False,
				# 'endPoint' : 'blArc.endPoint'
			# })
			# trArc = Arc({
				# 'startPoint' : 'outerSpiral.endPoint',
				# 'startAngle' : 'outerSpiral.endAngle',
				# 'radius' : 0.03 * i,
				# 'endAngle' : 'startAngle - 100',
				# 'id' : 'trArc',
				# 'reverse' : True
			# })
			# brArc = Arc({
				# 'startPoint' : 'innerSpiral.endPoint',
				# 'startAngle' : 'innerSpiral.endAngle + 180',
				# 'radius' : 0.02 * i,
				# 'endAngle' : 'startAngle + 70',
				# 'id' : 'brArc',
			# })
			# lArc = Arc({
				# 'startPoint' : 'tlArc.endPoint',
				# 'startAngle' : 'tlArc.endAngle',
				# 'reverse' : False,
				# 'endPoint' : 'blArc.endPoint'
			# })
