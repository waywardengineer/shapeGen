#!/usr/bin/env python
from flask import Flask, request, jsonify, Response
import json

from designs import *
# design = Nautilus3()
# design = Nautilus()
# design = Nautilus2()
# design = SpiraleyHolePanel()
# design = AlienSpineCircuitTraces()
# design = MultiDesign(ThreeArmThinSpiral, 10, 1)
# design = ThreeSidedPointyThing()
# design = TestDesign()
design = Something3()
# design = Something()
flaskApp = Flask(__name__,  static_folder='jsGui', static_url_path='/jsGui')

@flaskApp.route('/')
def jsGui():
	return flaskApp.send_static_file('index.htm')

@flaskApp.route('/getData', methods =['GET', 'POST'])
def getData():
	return jsonify(design.getCurrentStateData())

@flaskApp.route('/doCommand', methods =['POST'])
def doCommand():
	requestData = json.loads(request.data)
	command = requestData.pop(0)
	function = getattr(design, command)
	return jsonify({'command' : command, 'result' : function(*requestData)})

if __name__ == '__main__':
	flaskApp.run(debug = True, port=80) 
