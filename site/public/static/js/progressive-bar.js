var timeleft = 59;
var timetotal = 59;
var stop = false;
function FlagProgressBar() {
    stop = true;
}
function resetProgressBar(){
    timeleft = 59;
    timetotal = 59;
}
function progress(timeleft, timetotal, $element) {
    if (stop === true) {
        var progressBarWidth = timeleft * $element.width() / timetotal;
        $element.find('div').animate({ width: progressBarWidth }, 500).html(Math.floor(timeleft / 60) + ":" + timeleft % 60);
        if (timeleft > 0) {
            setTimeout(function () {
                progress(timeleft - 1, timetotal, $element);
            }, 1060);
        }
    }
};