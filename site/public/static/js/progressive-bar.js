var timeleft = 15;
var timetotal = 15;
var stop = false;

function FlagProgressBar() {
    stop = true;
}

function resetProgressBar(){
   
    timeleft = 15;
    timetotal = 15;
    document.getElementById("progressBar").hidden = true;     //hidden blu progress bar
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
    }
};