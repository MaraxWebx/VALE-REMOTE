'use strict';

var constraints = {
	audio: false,
	video: false
};

var recBtn = document.querySelector('button#rec');
//var timeView = document.querySelector('#answerTime');
//var pauseResBtn = document.querySelector('button#pauseRes');
var stopBtn = document.querySelector('button#stop');

var videoElement = document.querySelector('video');
var dataElement = document.querySelector('#data');
//var downloadLink = document.querySelector('a#downloadLink');
var flagStopBtn = false



var mediaRecorder;
var chunks = [];
var count = 0;
var localStream = null;
var soundMeter = null;
var is_recording = false;


document.getElementById("boxRis").hidden = true;

function stopStream() {
	if(!is_recording) return;
	is_recording = false;
	if(localStream !== undefined && localStream !== null){
		var tracks = localStream.getTracks();
		tracks.forEach(function (track) {
			console.log(tracks.length);
			track.stop();
		});
		videoElement.srcObject = null;
		console.log(constraints);
	}
}


function startCamera() {
	if(is_recording) return;
	is_recording = true;
	constraints = {
		audio: true,
		video: {
			width: { min: 320, ideal: 457, max: 457 },
			height: { min: 240, ideal: 420, max: 480 },
			framerate: 30
		}
	};
	if (!navigator.mediaDevices.getUserMedia) {
		alert('navigator.mediaDevices.getUserMedia not supported on your browser, use the latest version of Firefox or Chrome');
	} else {
		if (window.MediaRecorder == undefined) {
			alert('MediaRecorder not supported on your browser, use the latest version of Firefox or Chrome');
		} else {
			navigator.mediaDevices.getUserMedia(constraints)
				.then(function (stream) {
					localStream = stream;

					localStream.getTracks().forEach(function (track) {
						if (track.kind == "audio") {
							track.onended = function (event) {
								log("audio track.onended Audio track.readyState=" + track.readyState + ", track.muted=" + track.muted);
							}
						}
						if (track.kind == "video") {
							track.onended = function (event) {
								log("video track.onended Audio track.readyState=" + track.readyState + ", track.muted=" + track.muted);
							}
						}
					});

					videoElement.srcObject = localStream;
					videoElement.play();

					try {
						window.AudioContext = window.AudioContext || window.webkitAudioContext;
						window.audioContext = new AudioContext();
					} catch (e) {
						log('Web Audio API not supported.');
					}

					soundMeter = window.soundMeter = new SoundMeter(window.audioContext);
					soundMeter.connectToSource(localStream, function (e) {
						if (e) {
							log(e);
							return;
						} else {
							/*setInterval(function() {
							   log(Math.round(soundMeter.instant.toFixed(2) * 100));
						   }, 100);*/
						}
					});

				}).catch(function (err) {
					/* handle the error */
					log('navigator.getUserMedia error: ' + err);
				});
		}
	}
}

function create_UUID(){
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function onBtnRecordClicked() {
	if (localStream == null) {
		alert('Could not get local stream from mic/camera');
	} else {
		//progressBar.hidden = false;
		document.getElementById("time").hidden = false;
		//answerTime.hidden = false;
		recBtn.hidden = true;
		//pauseResBtn.disabled = false;
		stopBtn.hidden = false;
		//progress(60, 60, $('#progressBar'));		//set time to progress bar
		//startTimer(10, document.querySelector('#time'));

		/* use the stream */
		log('Start recording...');

		if (typeof MediaRecorder.isTypeSupported == 'function') {
			/*
				MediaRecorder.isTypeSupported is a function announced in https://developers.google.com/web/updates/2016/01/mediarecorder and later introduced in the MediaRecorder API spec http://www.w3.org/TR/mediastream-recording/
			*/
			if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
				var options = { mimeType: 'video/webm;codecs=vp9' };
			} else if (MediaRecorder.isTypeSupported('video/webm;codecs=h264')) {
				var options = { mimeType: 'video/webm;codecs=h264' };
			} else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8')) {
				var options = { mimeType: 'video/webm;codecs=vp8' };
			}
			log('Using ' + options.mimeType);
			mediaRecorder = new MediaRecorder(localStream, options);
		} else {
			log('isTypeSupported is not supported, using default codecs for browser');
			mediaRecorder = new MediaRecorder(localStream);
		}

		mediaRecorder.ondataavailable = function (e) {
			//log('mediaRecorder.ondataavailable, e.data.size='+e.data.size);
			chunks.push(e.data);
		};

		mediaRecorder.onerror = function (e) {
			log('mediaRecorder.onerror: ' + e);
		};

		mediaRecorder.onstart = function () {
			log('mediaRecorder.onstart, mediaRecorder.state = ' + mediaRecorder.state);

			localStream.getTracks().forEach(function (track) {
				if (track.kind == "audio") {
					log("onstart - Audio track.readyState=" + track.readyState + ", track.muted=" + track.muted);
				}
				if (track.kind == "video") {
					log("onstart - Video track.readyState=" + track.readyState + ", track.muted=" + track.muted);
				}
			});

		};

		mediaRecorder.onstop = function () {
			log('mediaRecorder.onstop, mediaRecorder.state = ' + mediaRecorder.state);

			var blob = new Blob(chunks, { type: "video/webm" });
			chunks = [];

			stopBtn.hidden = true;
			//downloadLink.innerHTML = '<button class="okButton" id="controls"><p>Scarica</p></button>';
			var d = new Date();
			var date = d.getDate() + "-" + d.getMonth() + "-" + d.getFullYear();
			var uuid = window.create_UUID();
			var name = "video_" + uuid + "_" + date + ".webm";
			let file = new File([blob], name, { type: "video/webm" });

			//downloadLink.setAttribute("download", file.name);
			//downloadLink.setAttribute("name", file.name);

			var videoURL = window.URL.createObjectURL(file);
			//downloadLink.href = videoURL;
			videoElement.src = videoURL;

			console.log(file);
			window.prepareSubmit(file);
			//window.submitFile(file);		
		};

		mediaRecorder.onpause = function () {
			log('mediaRecorder.onpause, mediaRecorder.state = ' + mediaRecorder.state);
		}

		/*mediaRecorder.onresume = function () {
			log('mediaRecorder.onresume, mediaRecorder.state = ' + mediaRecorder.state);
		}*/

		mediaRecorder.onwarning = function (e) {
			log('mediaRecorder.onwarning: ' + e);
		};

		//pauseResBtn.textContent = "Pause";

		mediaRecorder.start();

		localStream.getTracks().forEach(function (track) {
			log(track.kind + ":" + JSON.stringify(track.getSettings()));
			console.log(track.getSettings());
		})
	}
}

function onBtnStartClicked() {

	//progress(10, 10, $('#progressBar'));		//set time to progress bar
	enableCode();
	editor.getDoc().setValue('');
	//editor.getDoc().setValue('');
	editor.setOption("readOnly", false);
	document.getElementById("StartTextBtn").hidden = true;
	document.getElementById("ConfirmTextBtn").hidden = false;
}

function onBtnConfirmClicked() {

	disableCode();
	editor.setOption("readOnly", 'nocursor');
	
	/* if (window.flag) {
		document.getElementById("ConfirmTextBtn").hidden = true;		
	}
	document.getElementById("textArea").disabled = true; */


}

function enableCode(){
	$('.CodeMirror').css({
		opacity: 1
	})
}
function disableCode(){
	$('.CodeMirror').css({
		opacity: 0.3
	})
}

navigator.mediaDevices.ondevicechange = function (event) {
	log("mediaDevices.ondevicechange");
	/*
	if (localStream != null){
		localStream.getTracks().forEach(function(track) {
			if(track.kind == "audio"){
				track.onended = function(event){
					log("audio track.onended");
				}
			}
		});
	}
	*/
}

function onBtnStopClicked() {
	window.stop = false;
	window.resetProgressBar();
	flagStopBtn = true;
	mediaRecorder.stop();
	//window.question();
	//recBtn.disabled = false;
	//progressBar.hidden = false;
	//pauseResBtn.disabled = true;
	//stopBtn.disabled = true;
	//timeBox.hidden = true;
	//timeView.hidden = true;

}

/*function onPauseResumeClicked() {
	if (pauseResBtn.textContent === "Pause") {
		pauseResBtn.textContent = "Resume";
		mediaRecorder.pause();
		stopBtn.disabled = true;
	} else {
		pauseResBtn.textContent = "Pause";
		mediaRecorder.resume();
		stopBtn.disabled = false;
	}
	recBtn.disabled = true;
	pauseResBtn.disabled = false;
}

function onStateClicked() {

	if (mediaRecorder != null && localStream != null && soundMeter != null) {
		log("mediaRecorder.state=" + mediaRecorder.state);
		log("mediaRecorder.mimeType=" + mediaRecorder.mimeType);
		log("mediaRecorder.videoBitsPerSecond=" + mediaRecorder.videoBitsPerSecond);
		log("mediaRecorder.audioBitsPerSecond=" + mediaRecorder.audioBitsPerSecond);

		localStream.getTracks().forEach(function (track) {
			if (track.kind == "audio") {
				log("Audio: track.readyState=" + track.readyState + ", track.muted=" + track.muted);
			}
			if (track.kind == "video") {
				log("Video: track.readyState=" + track.readyState + ", track.muted=" + track.muted);
			}
		});

		log("Audio activity: " + Math.round(soundMeter.instant.toFixed(2) * 100));
	}

}*/

function log(message) {
	//dataElement.innerHTML = dataElement.innerHTML + '<br>' + message;   //delete this when you'll end
	//console.log(message); //delete this when you'll end
}

// Meter class that generates a number correlated to audio volume.
// The meter class itself displays nothing, but it makes the
// instantaneous and time-decaying volumes available for inspection.
// It also reports on the fraction of samples that were at or near
// the top of the measurement range.
function SoundMeter(context) {
	this.context = context;
	this.instant = 0.0;
	this.slow = 0.0;
	this.clip = 0.0;
	this.script = context.createScriptProcessor(2048, 1, 1);
	var that = this;
	this.script.onaudioprocess = function (event) {
		var input = event.inputBuffer.getChannelData(0);
		var i;
		var sum = 0.0;
		var clipcount = 0;
		for (i = 0; i < input.length; ++i) {
			sum += input[i] * input[i];
			if (Math.abs(input[i]) > 0.99) {
				clipcount += 1;
			}
		}
		that.instant = Math.sqrt(sum / input.length);
		that.slow = 0.95 * that.slow + 0.05 * that.instant;
		that.clip = clipcount / input.length;
	};
}

SoundMeter.prototype.connectToSource = function (stream, callback) {
	console.log('SoundMeter connecting');
	try {
		this.mic = this.context.createMediaStreamSource(stream);
		this.mic.connect(this.script);
		// necessary to make sample run, but should not be.
		this.script.connect(this.context.destination);
		if (typeof callback !== 'undefined') {
			callback(null);
		}
	} catch (e) {
		console.error(e);
		if (typeof callback !== 'undefined') {
			callback(e);
		}
	}
};
SoundMeter.prototype.stop = function () {
	this.mic.disconnect();
	this.script.disconnect();
};


//browser ID
function getBrowser() {
	var nVer = navigator.appVersion;
	var nAgt = navigator.userAgent;
	var browserName = navigator.appName;
	var fullVersion = '' + parseFloat(navigator.appVersion);
	var majorVersion = parseInt(navigator.appVersion, 10);
	var nameOffset, verOffset, ix;

	// In Opera, the true version is after "Opera" or after "Version"
	if ((verOffset = nAgt.indexOf("Opera")) != -1) {
		browserName = "Opera";
		fullVersion = nAgt.substring(verOffset + 6);
		if ((verOffset = nAgt.indexOf("Version")) != -1)
			fullVersion = nAgt.substring(verOffset + 8);
	}
	// In MSIE, the true version is after "MSIE" in userAgent
	else if ((verOffset = nAgt.indexOf("MSIE")) != -1) {
		browserName = "Microsoft Internet Explorer";
		fullVersion = nAgt.substring(verOffset + 5);
	}
	// In Chrome, the true version is after "Chrome"
	else if ((verOffset = nAgt.indexOf("Chrome")) != -1) {
		browserName = "Chrome";
		fullVersion = nAgt.substring(verOffset + 7);
	}
	// In Safari, the true version is after "Safari" or after "Version"
	else if ((verOffset = nAgt.indexOf("Safari")) != -1) {
		browserName = "Safari";
		fullVersion = nAgt.substring(verOffset + 7);
		if ((verOffset = nAgt.indexOf("Version")) != -1)
			fullVersion = nAgt.substring(verOffset + 8);
	}
	// In Firefox, the true version is after "Firefox"
	else if ((verOffset = nAgt.indexOf("Firefox")) != -1) {
		browserName = "Firefox";
		fullVersion = nAgt.substring(verOffset + 8);
	}
	// In most other browsers, "name/version" is at the end of userAgent
	else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) <
		(verOffset = nAgt.lastIndexOf('/'))) {
		browserName = nAgt.substring(nameOffset, verOffset);
		fullVersion = nAgt.substring(verOffset + 1);
		if (browserName.toLowerCase() == browserName.toUpperCase()) {
			browserName = navigator.appName;
		}
	}
	// trim the fullVersion string at semicolon/space if present
	if ((ix = fullVersion.indexOf(";")) != -1)
		fullVersion = fullVersion.substring(0, ix);
	if ((ix = fullVersion.indexOf(" ")) != -1)
		fullVersion = fullVersion.substring(0, ix);

	majorVersion = parseInt('' + fullVersion, 10);
	if (isNaN(majorVersion)) {
		fullVersion = '' + parseFloat(navigator.appVersion);
		majorVersion = parseInt(navigator.appVersion, 10);
	}


	return browserName;
}
