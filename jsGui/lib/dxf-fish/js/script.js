
var settings = {
	'serverUrl' : '/'
};
var currentStateData = false;


function sqr(wert){
return wert*wert;
}

function un_komma(string){
return string.replace(/\,/,".");
}

function komma(number){
return number.replace(/\./,",");
}




function dxf_lesen(text){
	worker = new Worker("jsGui/lib/dxf-fish/js/dxf-reader.js");
	worker.addEventListener('message',message_from_worker, false);
	worker.addEventListener('error',error_in_worker, false);
	message_to_worker('laden',text);
	show_loading();
}

function message_to_worker(cmd, daten){
	worker.postMessage({'cmd': cmd, 'daten': daten});
}

function message_from_worker(event){
	if (event.data.cmd == 'fertig'){
		 drawing = event.data.daten[0];
		 layers = event.data.daten[1];
		 available_blocks = event.data.daten[2];
		 meta = event.data.daten[3];
		 finish_loading();
		 draw();
		 return
	 }
	 if (event.data.cmd == 'echo'){
		console.log(event.data.daten);
	 }
}

function error_in_worker(){

}

function show_loading(){
	$('body').addClass("overlay").append("<img id='loader' src='jsGui/images/ajax-loader.gif' />");
}

function finish_loading(){
	$("#loader").remove();
	$('body').removeClass("overlay");
}