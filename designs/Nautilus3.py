from DesignBase import Design
from shapes import *
import json

def interpolate(factor, limits):
	return limits[0] + factor * (limits[1] - limits[0])

class Nautilus3(Design):
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
			holeSpiral = Spiral({
				'rotationAngle' : 0,
				'sweepStartAngle' : startAngle + 5,
				'centerPoint' : (0, 0),
				'scaleFactor' : interpolate(0.57, (innerScaleFactor, outerScaleFactor)),
				'growthFactorAdjustment' : interpolate(0.57, (innerGrowthFactor, outerGrowthFactor)),
				'sweepAngleSpan' : angleSpan - 10,
				'reverse' : True,
				'id' : 'holeSpiral'
			})
			lowerRadius = 0.25 * (outerSpiral.getRadius(startAngle) - innerSpiral.getRadius(startAngle))
			upperRadius = 0.25 * (outerSpiral.getRadius(startAngle + angleSpan) - innerSpiral.getRadius(startAngle + angleSpan))
			holes = HolesOnArcChain(ShapeGroup('holeSpiralGroup', holeSpiral), {
				'holeDistance' : 0.24 - (startAngle/3000)**1.8, 
				'holeRadii' : [lowerRadius, upperRadius],
				'minRadius' : 0.055,
				'id' : 'holes'
			})
			segment = ShapeGroup('segment' + str(i), innerSpiral, outerSpiral, holes, lArc, rArc)
			spirals.addSubShape(segment)
		i = 0
		while i < 12:
			makeSegment(0, 1, i * spiralInterval, spiralAngleSpan)
			i += 1
		topShape = ShapeGroup('top', spirals)
		self.shapes.append(topShape)
		Design.build(self)
