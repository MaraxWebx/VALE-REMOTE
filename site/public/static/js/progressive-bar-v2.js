
var progress_time = 180;
var progress_id;
var timeleft=0;

function restart_progress_timer(){
    clearInterval(progress_id)
    display_progress = document.querySelector("#progressBar")
    start_timer(display_progress, progress_time)
}

function set_progress_timer(time){
    progress_time = time;
}

function countdown_timer_finished(){
    clearInterval(progress_id)
    window.onBtnStopClicked(); 
    window.btnStop(); 
    window.question(); 
}

function stop_progress_timer(){
    clearInterval(progress_id);
    document.querySelector("#progressBar").textContent = ''
}

function start_progress_timer(display_progress, duration){
    timeleft = duration
    var minutes, seconds;
    if (timeleft < 0) {
        display_progress.textContent = "Tempo scaduto!";
        countdown_timer_finished()
        timeleft = duration;
        return;
    }
    minutes = parseInt(timeleft / 60, 10);
    seconds = parseInt(timeleft % 60, 10);

    display_progress.innerHTML = ""
    if(minutes == 0 && seconds <= 15){
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display_progress.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes + ":" + seconds + "</h3>";
    }else{
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display_progress.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes + ":" + seconds + "</h3>";
    }

    timeleft--;
    progress_id = setInterval(function () {
        if (timeleft < 0) {
            display_progress.textContent = "Tempo scaduto!";
            countdown_timer_finished()
            timeleft = duration;
            return;
        }
        minutes = parseInt(timeleft / 60, 10);
        seconds = parseInt(timeleft % 60, 10);
        display_progress.innerHTML = ""
        if(minutes == 0 && seconds <= 15){
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
    
            display_progress.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes + ":" + seconds + "</h3>";
        }else{
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
    
            display_progress.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes + ":" + seconds + "</h3>";
        }

        timeleft--;
    }, 1000);

}