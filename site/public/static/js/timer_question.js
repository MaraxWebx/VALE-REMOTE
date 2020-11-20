
var question_time = 10;
var timer_id;

function restart_timer(){
    display = document.querySelector("#timer_time_left")
    start_timer(display, question_time)
}

function countdown_finished(){
    clearInterval(timer_id)
    // Gestire fine del tempo!

}

function start_timer(display, duration){
    var timer = duration, minutes, seconds;
    timer_id = setInterval(function () {
        if (timer < 0) {
            display.textContent = "Tempo scaduto!";
            countdown_finished()
            timer = duration;
            return;
        }
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = "Tempo rimanente: " + minutes + ":" + seconds;

        timer--;

        
    }, 1000);

}