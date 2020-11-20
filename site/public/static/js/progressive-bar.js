var timeleft = 30;
var timetotal = 30;
var stop = false;

function FlagProgressBar() {
    stop = true;
}

function resetProgressBar(){
    timeleft = 30;
    timetotal = 30;
}

function resetProgressBar(time){
    timeleft = time;
    timetotal = time;
}

function progress(timeleft, timetotal, $element) {
    if (stop === true) {
        document.getElementById("progressBar").hidden = false;
        var progressBarWidth = timeleft * $element.width() / timetotal;
        $('#bar').animate({ width: progressBarWidth }, 500);
        $('#time').html(Math.floor(timeleft / 60) + ":" + timeleft % 60);
        if (timeleft > 0) {
            setTimeout(function () {
                progress(timeleft - 1, timetotal, $element);
            }, 1060);
        }
        if (progressBarWidth === 0) {
            onBtnStopClicked(); 
            window.btnStop(); 
            window.question(); 
            document.getElementById("time").hidden = true;
        }
    }
};

function progress_auto_record(timeleft_auto, timetotal_auto, $element){
    if (window.user_start_record === false) {
        document.getElementById("progressBar").hidden = false;
        var progressBarWidth = timeleft_auto * $element.width() / timetotal_auto;
        $('#bar_auto').animate({ width: progressBarWidth }, 500);
        $('#time_auto').html(Math.floor(timeleft_auto / 60) + ":" + timeleft_auto % 60);
        if (timeleft_auto > 0) {
            setTimeout(function () {
                progress_auto_record(timeleft_auto - 1, timetotal_auto, $element);
            }, 1060);
        }
        if (progressBarWidth === 0) {
            window.user_start_record === true;
            FlagProgressBar();
            progress(window.timeleft, window.timetotal, $element);
            window.onBtnRecordClicked(); 
            window.runSpeechRecognition();
        }
    }
}