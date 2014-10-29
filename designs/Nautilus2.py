from DesignBase import Design
from shapes import *
import json

def interpolate(factor, limits):
	return limits[0] + factor * (limits[1] - limits[0])

class Nautilus2(Design):
	def build(self):
		self.shapes = []
		spirals = ShapeGroup('apirals')
		spiralAngleSpan = 65.
		spiralSpacing = 5.
		spiralInterval = spiralAngleSpan + spiralSpacing
		scaleFactors = (0.125, 0.125)
		growthFactors = (0.5, 0.707)
		def makeSegment(innerSizeFactor, outerSizeFactor, startAngle, angleSpan):
			innerGrowthFactor = interpolate(innerSizeFactor, growthFactors)
			outerGrowthFactor = interpolate(outerSizeFactor, growthFactors)
			innerScaleFactor = interpolate(innerSizeFactor, scaleFactors)
			outerScaleFactor = interpolate(outerSizeFactor, scaleFactors)
			innerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : startAngle,
				'centerPoint' : (0, 0),
				'scaleFactor' : innerScaleFactor,
				'growthFactorAdjustment' : innerGrowthFactor,
				'sweepAngleSpan' : angleSpan,
				'reverse' : True,
				'id' : 'innerSpiral'
			})
			outerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : startAngle,
				'centerPoint' : (0, 0),
				'scaleFactor' : outerScaleFactor,
				'growthFactorAdjustment' : outerGrowthFactor,
				'sweepAngleSpan' : angleSpan,
				'reverse' : True,
				'id' : 'outerSpiral'
			})
			lArc = Arc({
				'startPoint' : '%outerSpiral.endPoint',
				'startAngle' : '%outerSpiral.endAngle + 30',
				'reverse' : False,
				'endPoint' : '%innerSpiral.endPoint'
			})
			rArc = Arc({
				'startPoint' : '%outerSpiral.startPoint',
				'startAngle' : '%outerSpiral.startAngle + 30',
				'reverse' : False,
				'endPoint' : '%innerSpiral.startPoint'
			})
			segment = ShapeGroup('segment' + str(i), innerSpiral, outerSpiral, lArc, rArc)
			spirals.addSubShape(segment)
		i = 0
		while i < 6:
			makeSegment(0, 1, i * spiralInterval, spiralAngleSpan)
			i += 1
		makeSegment(0.52, 1, i * spiralInterval, (spiralAngleSpan / 2) - spiralSpacing)
		while i < 8:
			makeSegment(0, 0.5, i * spiralInterval, spiralAngleSpan)
			makeSegment(0.52, 1, i * spiralInterval + spiralAngleSpan / 2, spiralAngleSpan)
			i += 1
		makeSegment(0.77, 1, i * spiralInterval + spiralAngleSpan / 2, (spiralAngleSpan / 2) - spiralSpacing)
		while i < 10:
			makeSegment(0, 0.5, i * spiralInterval, spiralAngleSpan)
			makeSegment(0.52, 0.75, i * spiralInterval + spiralAngleSpan / 2, spiralAngleSpan)
			makeSegment(0.77, 1, i * spiralInterval + spiralAngleSpan, spiralAngleSpan)
			i += 1
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
