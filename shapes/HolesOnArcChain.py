from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *
from shapes import Circle
class HolesOnArcChain(Shape):
	def __init__(self, arcChain, *args):
		Shape.__init__(self, *args)
		self.addSubShape(arcChain)
		self.subShapes[0].updateParam('dontRenderSubShapes', True)

	def calculate(self):
		def calculateNextRadius(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			arcLengthUsed = sum([arcs[i].p.arcLength for i in range(currentArcIndex)])
			if arc.p.type == 'Arc':
				arcLengthUsed += (angleOnArc / arc.p.angleSpan) * arc.p.arcLength
			elif arc.p.type == 'Spiral':
				arcLengthUsed += arc.lookupArcLength(angleOnArc)
			interval = totalArcLength / (len(self.p.holeRadii) - 1.)
			angle = (pi / 2) * ((arcLengthUsed % interval) / interval)
			radiusIndex = int(arcLengthUsed // interval)
			if (radiusIndex + 1) >= len(self.p.holeRadii):
				nextRadiusIndex = radiusIndex
			else:
				nextRadiusIndex = radiusIndex + 1
			radius = self.p.holeRadii[radiusIndex] + sin(angle) * (self.p.holeRadii[nextRadiusIndex] - self.p.holeRadii[radiusIndex])
			return radius

		def calculateNextAngleIncrement(arcIndex, angleOnArc, distanceToNextHole):
			arc = arcs[arcIndex]
			if arc.p.type == 'Arc':
				radius = arc.p.radius
			elif arc.p.type == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			ratio = distanceToNextHole / (2 * radius)
			if ratio > 1:
				return 180
			angleIncrement = 2 * degrees(asin(ratio))
			return angleIncrement

		def getCenterPoint(arcIndex, angleOnArc):
			arc = arcs[arcIndex]
			if arc.p.type == 'Spiral':
				startAngle = arc.p.rotationAngle
			else:
				startAngle = arc.p.startAngle
			if arc.p.reverse:
				angle = startAngle - angleOnArc
			else:
				angle = startAngle + angleOnArc
			if arc.p.type == 'Arc':
				radius = arc.p.radius
			elif arc.p.type == 'Spiral':
				radius = arc.getRadius(angleOnArc)
			vector = polarToCartesian((angle, radius))
			return (vector[0] + arc.p.centerPoint[0], vector[1] + arc.p.centerPoint[1])

		def transitionToNextArc(lastCenterPoint, targetDistanceToNextHole, newArcIndex):
			angle = 0.
			error = 500
			lastError = 1000
			while 5 < error < lastError:
				lastError = error
				newCenterPoint = getCenterPoint(newArcIndex, angle)
				distanceToNextHole = hypot(lastCenterPoint[0] - newCenterPoint[0], lastCenterPoint[1] - newCenterPoint[1])
				error = 100. * (targetDistanceToNextHole - distanceToNextHole) / targetDistanceToNextHole
				angle += 0.25
			return angle
		self.subShapes = [self.subShapes[0]]
		arcs = self.subShapes[0].subShapes
		totalArcLength = sum(arc.p.arcLength for arc in arcs)
		currentArcIndex = 0
		nextRadius = self.p.holeRadii[0]
		angleIncrement = 5
		while currentArcIndex < len(arcs):
			arc = arcs[currentArcIndex]
			if arc.p.type == 'Arc':
				endAngle = arc.p.angleSpan
				currentAngleOnArc = 0
			elif arc.p.type == 'Spiral':
				endAngle = arc.p.sweepEndAngle
				currentAngleOnArc = arc.p.sweepStartAngle
			while currentAngleOnArc < endAngle:
				thisRadius = nextRadius
				centerPoint = getCenterPoint(currentArcIndex, currentAngleOnArc)
				skip = False
				if thisRadius < self.p.minRadius:
					skip = True
				# skip = skip or distanceBetween(centerPoint, 
				if skip:
					print 'skipping'
				if not skip:
					self.subShapes.append(Circle({
						'centerPoint' : centerPoint,
						'radius' : thisRadius
					}))
				error = 100
				lastError = 200
				while 5 < error < lastError:
					distanceToNextHole = self.p.holeDistance + (thisRadius + nextRadius)
					angleIncrement = calculateNextAngleIncrement(currentArcIndex, currentAngleOnArc, distanceToNextHole)
					newNextRadius = calculateNextRadius(currentArcIndex, currentAngleOnArc + angleIncrement)
					lastError = error
					error = 100. * abs((nextRadius - newNextRadius) / newNextRadius)
					nextRadius = newNextRadius
				currentAngleOnArc += angleIncrement
			currentArcIndex += 1
			if currentArcIndex < len(arcs):
				currentAngleOnArc = transitionToNextArc(centerPoint, distanceToNextHole, currentArcIndex)