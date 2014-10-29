from dxfwrite import DXFEngine as dxf
from shapes import *
import json
from copy import copy

class Design(object):
	def __init__(self):
		self.fileName = 'output.dxf'
		self.paramDirectory = {}
		self.modifiedParams = {}
		self.shapes = []
		self.justLoaded = True

	def saveToFile(self):
		self.drawing = dxf.drawing(self.fileName)
		self.build()
		for shape in self.shapes:
			shape.addToDrawing(self.drawing)
		self.drawing.save()

	def getCurrentStateData(self):
		self.saveToFile()
		with open (self.fileName, "r") as file:
			drawingContents = file.read()
		paramDataList = []
		for id in self.paramDirectory.keys():
			item = self.paramDirectory[id]
			paramDataList += [{'id' : id + ':' + k, 'value' : item['object'].p[k].value} for k in item['changeableParams']]
		data = {
			'drawingContents' : drawingContents,
			'params' : {i['id'] : i['value'] for i in paramDataList} 
		}
		return data

	def build(self):
		paramDirectoryList = []
		for shape in self.shapes:
			paramDirectoryList += shape.getParamDirectory()
		self.paramDirectory = {d['id'] : d for d in paramDirectoryList}
		for id in self.modifiedParams.keys():
			(objectId, paramId) = id.split(':')
			self.paramDirectory[objectId]['object'].updateParam(paramId, self.modifiedParams[id])
		for shape in self.shapes:
			shape.build(shape)
			
	def updateValue(self, id, value):
		self.modifiedParams[id] = value

	def checkForReload(self):
		result = self.justLoaded
		self.justLoaded = False
		return result


class MultiDesign(Design):
	def __init__(self, designClass, count, increment):
		Design.__init__(self)
		self.designs = [designClass(i*increment) for i in range(count)]
		self.fileNameBase = designClass.__name__
		self.currentDesignIndex = 0
		for i in range(len(self.designs)):
			self.designs[i].fileName = self.fileNameBase + '_' + str(i) + '.dxf'
		self.saveToFile()

	def getCurrentStateData(self):
		data = self.designs[self.currentDesignIndex].getCurrentStateData()
		data['params']['currentDesignIndex'] = self.currentDesignIndex
		return data

	def saveToFile(self):
		for design in self.designs:
			design.saveToFile()

	def updateValue(self, id, value):
		if id not in ['currentDesignIndex']:
			self.designs[self.currentDesignIndex].updateValue(id, value)
		else:
			self.currentDesignIndex = int(value)
		
