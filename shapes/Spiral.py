from math import sin, cos, radians, pi, atan2, hypot, e, degrees, asin
from copy import deepcopy, copy
from dxfwrite import DXFEngine as dxf
from shapeUtils import *
from shapeBases import *

class Spiral(Shape):
	def getRadius(self, angleFromStart):
		b = 0.0053468
		radius = self.p.scaleFactor * pow(e, b * self.p.growthFactorAdjustment * angleFromStart)
		return radius

	def calculate(self, *args): 
		if not self.p.sweepStartAngle:
			self.p.sweepStartAngle = 0
		self.p.sweepEndAngle = self.p.sweepStartAngle + self.p.sweepAngleSpan
		self.points = []
		self.arcLengthLookup = []
		if self.p.reverse:
			direction = -1
		else:
			direction = 1
		arcLength = 0
		finished = False
		angleFromStart = self.p.sweepStartAngle
		while not finished:
			if angleFromStart > self.p.sweepEndAngle:
				angleFromStart = self.p.sweepEndAngle
			finished = angleFromStart >= self.p.sweepEndAngle
			radius = self.getRadius(angleFromStart)
			if not ('minRadius' in self.p.keys() and radius < self.p.minRadius):
				pointInPolar = (self.p.rotationAngle + direction * angleFromStart, radius)
				point = addVectors(polarToCartesian(pointInPolar), self.p.centerPoint)
				if len(self.points) > 0:
					arcLength += distanceBetween(point, self.points[-1])
					self.arcLengthLookup.append((angleFromStart, arcLength))
				self.points.append(point)
			angleFromStart += minLineSize / (sin(radians(1)) * radius)
		self.p.arcLength = arcLength
		self.p.endPoint = self.points[-1]
		self.p.endAngle = degrees(atan2(self.points[-1][1] - self.points[-2][1], self.points[-1][0] - self.points[-2][0])) + 90
		self.p.startPoint = self.points[0]
		self.p.startAngle = degrees(atan2(self.points[0][1] - self.points[1][1], self.points[0][0] - self.points[1][0])) + 90

	def lookupArcLength(self, angleFromStart):
		result = [i for i, v in enumerate(self.arcLengthLookup) if v[0] < angleFromStart]
		if len(result) == 0:
			return 0
		elif len(result) == len(self.arcLengthLookup):
			return self.p.arcLength
		else:
			return interpolate(angleFromStart, self.arcLengthLookup[result[-1]], self.arcLengthLookup[result[-1] + 1]) 
			
	def addToDrawing(self, drawing, layer='0'):
		for i in range(1, len(self.points)):
			line = dxf.line(self.points[i-1], self.points[i], layer=layer)
			drawing.add(line)