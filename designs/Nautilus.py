from .DesignBase import Design
from shapes import *
import json


class Nautilus(Design):
	def build(self):
		self.shapes = []
		spirals = ShapeGroup('apirals')
		spiralAngleSpan = 30
		spiralSpacing = 5
		for i in range(12):
			innerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : i * (spiralAngleSpan + spiralSpacing),
				'centerPoint' : (0, 0),
				'scaleFactor' : 0.5,
				'growthFactorAdjustment' : 0.5,
				'sweepAngleSpan' : spiralAngleSpan,
				'reverse' : True,
				'id' : 'innerSpiral'
			})
			outerSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : i * (spiralAngleSpan + spiralSpacing),
				'centerPoint' : (0, 0),
				'scaleFactor' : 0.5,
				'growthFactorAdjustment' : 1,
				'sweepAngleSpan' : spiralAngleSpan,
				'reverse' : True,
				'id' : 'outerSpiral'
			})
			lArc = Arc({
				'startPoint' : '%outerSpiral.endPoint',
				'startAngle' : '%outerSpiral.endAngle - 70',
				'reverse' : True,
				'endPoint' : '%innerSpiral.endPoint'
			})
			rArc = Arc({
				'startPoint' : '%outerSpiral.startPoint',
				'startAngle' : '%outerSpiral.startAngle - 70',
				'reverse' : True,
				'endPoint' : '%innerSpiral.startPoint'
			})
			circle = Circle({
				'centerPoint' : 'avgPoints(%outerSpiral.endPoint , %innerSpiral.startPoint )',
				'radius' : 'distanceBetween(%outerSpiral.startPoint , %innerSpiral.startPoint ) / 4'
			})
			segment = ShapeGroup('segment' + str(i), innerSpiral, outerSpiral, lArc, rArc, circle)
			spirals.addSubShape(segment)
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
