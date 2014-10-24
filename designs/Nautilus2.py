from DesignBase import Design
from shapes import *
import json


class Nautilus2(Design):
	def build(self):
		self.shapes = []
		spirals = ShapeGroup('apirals')
		spiralAngleSpan = 35.
		spiralSpacing = 5.
		spiralInterval = spiralAngleSpan + spiralSpacing
		def makeSegment(innerGrowthFactor, outerGrowthFactor, startAngle, angleSpan):
			innerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : startAngle,
				'centerPoint' : (0, 0),
				'scaleFactor' : 0.5,
				'growthFactorAdjustment' : innerGrowthFactor,
				'sweepAngleSpan' : angleSpan,
				'reverse' : True,
				'id' : 'innerSpiral'
			})
			outerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : startAngle,
				'centerPoint' : (0, 0),
				'scaleFactor' : 0.5,
				'growthFactorAdjustment' : outerGrowthFactor,
				'sweepAngleSpan' : angleSpan,
				'reverse' : True,
				'id' : 'outerSpiral'
			})
			lArc = Arc({
				'startPoint' : 'outerSpiral.endPoint',
				'startAngle' : 'outerSpiral.endAngle + 40',
				'reverse' : False,
				'endPoint' : 'innerSpiral.endPoint'
			})
			rArc = Arc({
				'startPoint' : 'outerSpiral.startPoint',
				'startAngle' : 'outerSpiral.startAngle - 50',
				'reverse' : True,
				'endPoint' : 'innerSpiral.startPoint'
			})
			segment = ShapeGroup('segment' + str(i), innerSpiral, outerSpiral, lArc, rArc)
			spirals.addSubShape(segment)
		for i in range(3):
			makeSegment(0.5, 1, i * spiralInterval, spiralAngleSpan)
		makeSegment(0.78, 1, 3 * spiralInterval, (spiralAngleSpan / 2) - spiralSpacing)
		for i in range(3, 10):
			makeSegment(0.5, 0.72, i * spiralInterval, spiralAngleSpan)
			makeSegment(0.78, 1, i * spiralInterval + spiralAngleSpan / 2, spiralAngleSpan)
		makeSegment(0.90, 1, 10 * spiralInterval + spiralAngleSpan / 2, (spiralAngleSpan / 2) - spiralSpacing)
		for i in range(10, 16):
			makeSegment(0.5, 0.72, i * spiralInterval, spiralAngleSpan)
			makeSegment(0.76, 0.88, i * spiralInterval + spiralAngleSpan / 2, spiralAngleSpan)
			makeSegment(0.90, 1, i * spiralInterval + spiralAngleSpan, spiralAngleSpan)
		topShape = ShapeGroup('top', spirals)
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
