comm = require('./lib/comm')
events = require('./lib/events')
display = require('./lib/display')

$(document).ready(function () {
	events.initEvents();
	comm.initOptions();
	comm.initMetaData();
	display.initDisplay();
})

