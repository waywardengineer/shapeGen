from DesignBase import Design
from shapes import *
import json
from shapes.shapeUtils import *

class SpiraleyHolePanel(Design):
	def build(self):
		def makeHoleChain(arcChain, id=False, holeradii=[0.125, 0.125, 0.2, 0.3, 0.4]):
			if not id:
				id = 'holes' + str(self.holeChainCount)
			holes = HolesOnArcChain(arcChain, {
				'holeDistance' : 0.3, 
				'holeRadii' : holeradii,
				'minRadius' : 0.125,
				'id' : id 
			})
			topShape.addSubShape(holes)
			self.holeChainCount += 1
			return holes
		self.holeChainCount = 0
		self.shapes = []
		topShape = ShapeGroup('topshape')
		topShape.addSubShape(Circle({'id' : 'heater', 'centerPoint' : (0, 39), 'radius' : 7}))
		topShape.addSubShape(Circle({'id' : 'board', 'centerPoint' : (33, 0), 'radius' : 10}))
		arcChain = ArcChain('arcChain', [{
			'startPoint' : (16, 0),
			'startAngle' : 185, 
			'angleSpan' : 60, 
			'radius' : 13,
			'reverse' : True,
		},{
			'angleSpan' : 105,
			'radius' : 25,
		},{
			'angleSpan' : 30,
			'radius' : 50,
		}])
		topShape.addSubShape(arcChain)
		arcChain.p.excludeSubShapes = True
		for i in range(5):
			offset = OffsetArcChain(arcChain, {
				'id' : 'offset' + str(i),
				'offset' : -1 * i - 0.5,
			})
			offset.transform(angle = 1 + 2 * i)
			offset.transform(distance = (0, -0.5 * i))
			smallholes = HolesOnArcChain(offset, {
				'holeDistance' : 2, 
				'holeRadii' : [0.01, 0.1, 0.3, 0.2, 0.2, 0.4, 0.5],
				'minRadius' : 0.06,
				'id' : 'little' + str(i) 
			})
			topShape.addSubShape(smallholes)
			offset = OffsetArcChain(arcChain, {
				'id' : 'offset' + str(i),
				'offset' : -1 * i,
			})
			offset.transform(angle = 2 * i)
			offset.transform(distance = (0, -0.5 * i))
			holes = makeHoleChain(offset, 'big' + str(i))
			if i==2:
				smallholes.p.startTrim = 1
			if i==3:
				holes.p.startTrim = 19
				smallholes.p.startTrim = 3
			if i==4:
				holes.p.startTrim = 38
				smallholes.p.startTrim = 5
		offset = OffsetArcChain(arcChain, {
			'id' : 'offset' + str(i),
			'offset' : -5.5,
		})
		offset.transform(angle = 11.5)
		offset.transform(distance = (1, -4))
		smallholes = HolesOnArcChain(offset, {
			'holeDistance' : 2, 
			'holeRadii' : [0.01, 0.01, 0.01, 0.01, 0.1, 0.3, 0.3, 0.4, 0.5],
			'minRadius' : 0.06,
			'id' : 'little5' 
		})
		topShape.addSubShape(smallholes)
		spiral = Spiral({
			'rotationAngle' : 0,
			'centerPoint' : (0, 0),
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 720,
			'reverse' : False,
			'id' : 'spiral4'
		})
		holes = makeHoleChain(ShapeGroup('group', spiral), False, [0.125, 0.125,0.3,  0.2, 0.125])
		holes.transform(angle = '%big4.startAngle - %endAngle + 180')
		holes.transform(distance = 'subtractVectors (%big4.startPoint , %endPoint )')
		spiral = Spiral({
			'rotationAngle' : 0,
			'centerPoint' : (0, 0),
			'scaleFactor' : 0.8,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 650,
			'reverse' : False,
			'id' : 'spiral3'
		})
		holes = makeHoleChain(ShapeGroup('group', spiral), False, [0.125, 0.125,0.3,  0.2, 0.125])
		holes.transform(angle = '%big3.startAngle - %endAngle + 180')
		holes.transform(distance = 'subtractVectors (%big3.startPoint , %endPoint )')
		arcChain = ArcChain('arcChain', [{
			'rotationAngle' : -100,
			'centerPoint' : '%spiral3.centerPoint',
			'scaleFactor' : 0.8,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 690,
			'reverse' : False
		},{
			'angleSpan' : 60,
			'radius' :15,
		}])
		makeHoleChain(arcChain, False, [0.125, 0.125, 0.3, 0.2])
		arcChain = ArcChain('arcChain', [{
			'rotationAngle' : -195,
			'centerPoint' : '%spiral4.centerPoint',
			'scaleFactor' : 1,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 720,
			'reverse' : False
		},{
			'angleSpan' : 19,
			'radius' :30,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 35,
			'radius' :15,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,
			'radius' :15,
		}])
		makeHoleChain(arcChain, False,  [0.125, 0.2, 0.2])
		arcChain = ArcChain('arcChain', [{
			'rotationAngle' : -231,
			'centerPoint' : (16, 31),
			'scaleFactor' : 0.7,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 725,
			'reverse' : False
		},{
			'angleSpan' : 32,
			'radius' :22,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 20,
			'radius' : 35,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 20,
			'radius' : 22,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 60,
			'radius' : 15,
		}])
		makeHoleChain(arcChain, 'topSpiral', [0.125, 0.2, 0.2])
		arcChain = ArcChain('arcChain', [{ #up from spiral
			'rotationAngle' : -60,
			'centerPoint' : '%topSpiral.arcChain.arc0.centerPoint',
			'scaleFactor' : 0.7,
			'growthFactorAdjustment' : 0.5,
			'sweepAngleSpan' : 790,
			'reverse' : False
		},{
			'angleSpan' : 62,
			'radius' :17,
			'noDirectionAlternate' : True
		},{
			'angleSpan' : 30,
			'radius' : 40,
			'noDirectionAlternate' : False
		}])
		makeHoleChain(arcChain)
		arcChain = ArcChain('arcChain', [{
			'startPoint' : (0.5, -2),
			'startAngle' : -16, 
			'angleSpan' : 25, 
			'radius' : 18,
			'reverse' : False,
		},{
			'angleSpan' : 49,
			'radius' :35,
		},{
			'angleSpan' : 97,
			'radius' : 8.7,
			# 'noDirectionAlternate' : True
		},{
			'angleSpan' : 25,
			'radius' : 50,
		}])
		makeHoleChain(arcChain, False, [0.2, 0.2, 0.3, 0.4])
		topShape.addSubShape(Line({'startPoint' : (0, 0), 'endPoint' : (33, 0)}))
		topShape.addSubShape(Line({'startPoint' : (33, 0), 'endPoint' : (33, 70)}))
		topShape.addSubShape(Line({'startPoint' : (33, 70), 'endPoint' : (0, 70)}))
		topShape.addSubShape(Line({'startPoint' : (0, 70), 'endPoint' : (0, 0)}))
		self.shapes.append(topShape)
		Design.build(self)
