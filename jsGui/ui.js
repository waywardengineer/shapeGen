

paramIds = [];
function doInit(){
	canvas = document.getElementById('canvas');
	canvas.width = window.innerWidth -275;
	canvas.height = window.innerHeight -15; 
	ctx = canvas.getContext('2d');
	$('#redrawButton').button().click(function(e){
		getLatestData();
	});
	getLatestData();
}
function getLatestData(){
	$.ajax(settings.serverUrl + 'getData', {
		dataType: 'json'
	}).done(function(result) {
		currentStateData = result;
		updateDisplay();
	});

}


function updateDisplay(){
	if (currentStateData.drawingContents){
		dxf_lesen(currentStateData.drawingContents);
	}
	inputHtml = ''
	paramIdNum = 0;
	paramIds = []
	$.each(currentStateData.params, function(paramId, paramData){
		inputHtml += '<label for="' + paramIdNum + '">' + paramId + '</label><input id="' + paramIdNum + '" value=' + paramData + ' class="paramInput ui-widget  ui-widget-content ui-corner-all"><br>';
		paramIds.push(paramId);
		paramIdNum ++;
	});
	$('#inputs').html(inputHtml);
	$('.paramInput').change(function(e){
		doCommand(['updateValue', paramIds[parseInt(this.id)], parseFloat($('#' + this.id).val())]);
	});
}
function doCommand(command){
	commandStr = JSON.stringify(command)
	$.ajax(settings.serverUrl + 'doCommand', {
		data : commandStr,
		contentType : 'application/json',
		type : 'POST',
		dataType: 'json',
	}).done(function(result) {
		handleCommandResult(result);
	});
}
function handleCommandResult(result){
}
