
var progress_time = 180;
var progress_id;
var timeleft=0;

function restart_progress_timer(){
    clearInterval(progress_id)
    display_progress = document.querySelector("#progressBar")
    start_progress_timer(display_progress, progress_time)
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

function start_progress_timer(display_progress, duration_progress){
    timeleft = duration_progress
    var minutes_progress, seconds_progress;
    if (timeleft < 0) {
        display_progress.textContent = "Tempo scaduto!";
        countdown_timer_finished()
        timeleft = duration_progress;
        return;
    }
    minutes_progress = parseInt(timeleft / 60, 10);
    seconds_progress = parseInt(timeleft % 60, 10);

    display_progress.innerHTML = ""
    if(minutes_progress == 0 && seconds_progress <= 15){
        minutes_progress = minutes_progress < 10 ? "0" + minutes_progress : minutes_progress;
        seconds_progress = seconds_progress < 10 ? "0" + seconds_progress : seconds_progress;

        display_progress.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes_progress + ":" + seconds_progress + "</h3>";
    }else{
        minutes_progress = minutes_progress < 10 ? "0" + minutes_progress : minutes_progress;
        seconds_progress = seconds_progress < 10 ? "0" + seconds_progress : seconds_progress;

        display_progress.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes_progress + ":" + seconds_progress + "</h3>";
    }

    timeleft--;
    progress_id = setInterval(function () {
        if (timeleft < 0) {
            display_progress.textContent = "Tempo scaduto!";
            countdown_timer_finished()
            timeleft = duration_progress;
            return;
        }
        minutes_progress = parseInt(timeleft / 60, 10);
        seconds_progress = parseInt(timeleft % 60, 10);
        display_progress.innerHTML = ""
        if(minutes_progress == 0 && seconds_progress <= 15){
            minutes_progress = minutes_progress < 10 ? "0" + minutes_progress : minutes_progress;
            seconds_progress = seconds_progress < 10 ? "0" + seconds_progress : seconds_progress;
    
            display_progress.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes_progress + ":" + seconds_progress + "</h3>";
        }else{
            minutes_progress = minutes_progress < 10 ? "0" + minutes_progress : minutes_progress;
            seconds_progress = seconds_progress < 10 ? "0" + seconds_progress : seconds_progress;
    
            display_progress.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes_progress + ":" + seconds_progress + "</h3>";
        }

        timeleft--;
    }, 1000);

}