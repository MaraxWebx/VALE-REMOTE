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

function start_progress(timeleft, timetotal, $element){
    if( timetotal >= window.timer){
        timetotal = window.timer-1;
        timeleft = window.timer-1;    
    }
    progress(timeleft, timetotal, $element);
}

function progress(timeleft, timetotal, $element) {
    if (stop === true) {
        document.getElementById("progressBar").hidden = false;
        var progressBarWidth = timeleft * $element.width() / timetotal;
        $('.bar').animate({ width: progressBarWidth }, 500);
        $('.time').html(Math.floor(timeleft / 60) + ":" + timeleft % 60);
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