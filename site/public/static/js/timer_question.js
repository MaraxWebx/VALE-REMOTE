
var question_time = 180;
var timer_id;
var timer=0;

function restart_timer(){
    clearInterval(timer_id)
    display = document.querySelector("#timer_time_left")
    start_timer(display, question_time)
}

function countdown_finished(){
    clearInterval(timer_id)
    // Gestire fine del tempo!
    

}

function stop_timer(){
    clearInterval(timer_id);
    document.querySelector("#timer_time_left").textContent = ''
}

function start_timer(display, duration){
    timer = duration
    var minutes, seconds;
    if (timer < 0) {
        display.textContent = "Tempo scaduto!";
        countdown_finished()
        timer = duration;
        return;
    }
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    display.innerHTML = ""
    if(minutes == 0 && seconds <= 15){
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes + ":" + seconds + "</h3>";
    }else{
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes + ":" + seconds + "</h3>";
    }

    timer--;
    timer_id = setInterval(function () {
        if (timer < 0) {
            display.textContent = "Tempo scaduto!";
            countdown_finished()
            timer = duration;
            return;
        }
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);
        display.innerHTML = ""
        if(minutes == 0 && seconds <= 15){
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
    
            display.innerHTML = 'Tempo rimanente: <h3 style="color : #e60000;">' + minutes + ":" + seconds + "</h3>";
        }else{
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
    
            display.innerHTML = 'Tempo rimanente: <h3 style = "color: #476692;">' + minutes + ":" + seconds + "</h3>";
        }

        timer--;
    }, 1000);

}