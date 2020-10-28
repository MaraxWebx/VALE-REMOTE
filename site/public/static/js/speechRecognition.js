'use strict;'

var text;

function runSpeechRecognition() {
  // get output div reference
  var output = document.getElementById("output");
  // get action element reference
  var action = document.getElementById("action");
  // new speech recognition object
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
  var recognition = new SpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = false;

  // This runs when the speech recognition service starts
  recognition.onstart = function () {
    //action.innerHTML = "<small>listening, please speak...</small>";
    this.transcript = " ";

  };

  btnStop = function () {
    recognition.stop();

    // action.innerHTML = "<small>stop listening</small>";
    console.log("stop speech recognition");
  }

  // This runs when the speech recognition service returns result
  recognition.onresult = function (event) {
    this.transcript += event.results[event.results.length - 1][0].transcript;
    /* output.innerHTML = "<b>TRY TEXT AREA:</b> " + " " + this.transcript + " ";
    output.classList.remove("hide"); */
    console.log("TRASCRIZIONE: " + this.transcript);
  };

  recognition.onend = function () {
    text = this.transcript;

   /*  //SEND TO SERVER THE TRANSCRIPT
    axios.post('http://localhost:3000/speech', {
      //rejectUnauthorized: false,
      transcript: text,
    })
      .then(() => {
      }, (error) => {
        console.log(error);
      }); */
  }

  // start recognition
  recognition.start();
}