var id = 0;
var prev_question_id = "";
var textTmp;
var vidTmp;
var choice_length;
var acc = 0;
var flag = false;
var i = 1;

var codeType = ["javascript", "javascript", "python", "php", "clike", "htmlembedded"];
var editor =  CodeMirror.fromTextArea(document.getElementById("textArea"),{
  mode: codeType[0],
  lineNumbers: true,
  autoCloseBrackets: true,
  readOnly: 'nocursor',
  theme: 'darcula'
});


function question() {
  window.countdown_finished();
  document.getElementById("colVale").hidden = false;
  document.getElementById("boxRis").hidden = false;
  document.getElementById("start").hidden = true;
  document.getElementById("bfine").hidden = true;
  document.getElementById("questionSection").hidden = false;

  showSpinner();

  id = id + 1;
  if (id == 1) {
    
    axios.get('/next/', {
      params: {
        type: 'base'
      }
    })
      .then(function (response) {
        hideSpinner()
        console.log("status getQuestion: " + response.status);
        document.getElementById("boxRis").hidden = false;
        prev_question_id = response.data.id;
        question_type = response.data.type;
        choice_length = response.data.length;
        getQuestion(response.data);
      })
      .catch(function (error) {
        console.error("Error in get request:", error)
       
      });
  } else {

    if (question_type === 'video') {
      acc++;
      if (acc < 2) return;
      else acc = 0;
      console.log('Window.text: ' + window.text)
      console.log('Window.formData' + window.formData.get('file'))
      textTmp = window.text;
      vidTmp = "to_upload";
    }

    if (question_type === 'code') {
      textTmp = editor.getValue();
      textTmp = textTmp.replace(/\n/g, '<br>')
      textTmp = textTmp.replace(/\t/g, '  ')
      textTmp = '<pre>' + textTmp + '</pre>'
      console.log(textTmp)
      vidTmp = "no_video";
      editor.getDoc().setValue('');
    }

    if (question_type === 'check') {
      for (j = 0; j < choice_length; j++) {
        if (document.getElementById("" + j).checked) {
          var x = document.getElementById("" + j).value;
          textTmp = x;
          flag = true;
          break;
        }
      }
      if (!flag) {
        alert('Seleziona una risposta');
        return;
      }
      vidTmp = "no_video";
    }
    axios.get('/next/', {
      params: {

        question_id: prev_question_id,
        answer_text: textTmp,
        answer_vid: vidTmp
      }
    })
      .then(function (response) {
        hideSpinner()
        document.getElementById("boxRis").hidden = false;
        if (question_type === 'video') {
          window.submitFile()
        }
        prev_question_id = response.data.id;
        question_type = response.data.type;
        choice_length = response.data.length;
        getQuestion(response.data);
      })
      .catch(function (error) {
        console.error("Error in get request:", error)
        
      });
  }
}

function getQuestion(quest) {
  var out = ''
  var titleOut;

  if (quest.id !== undefined) {

    if (quest.type === 'video') {
      //start video/audio stream
      document.getElementById("progressBar").hidden = true;     //hidden blu progress bar
      window.startCamera();
      window.setTimeout("document.querySelector('button#rec').hidden = false", 2000);
      if(parseInt(choice_length) > 0) window.resetProgressBarValue(parseInt(choice_length))
      else window.resetProgressBar()
      document.getElementById("video").hidden = false;
      document.getElementById("code").hidden = true;
      document.getElementById("video").hidden = false;
      document.getElementById("check").hidden = true;
      document.getElementById("StartTextBtn").hidden = true;
      document.getElementById("ConfirmTextBtn").hidden = true;
      document.getElementById("timeBox").hidden = false;
      printRis();

    } else if (quest.type === 'code') {
      //stop video/audio stream
      if(parseInt(choice_length) > 0) editor.setOption("mode", codeType[parseInt(choice_length)])
      document.getElementById("progressBar").hidden = true;     //hidden blu progress bar
      window.stopStream();
      document.getElementById("video").hidden = true;
      document.getElementById("code").hidden = false;
      document.getElementById("check").hidden = true;
      document.querySelector('button#rec').hidden = true;
      document.getElementById("StartTextBtn").hidden = false;
      document.getElementById("ConfirmTextBtn").hidden = true;
      document.getElementById("timeBox").hidden = true;
      

      printRis();

    } else if (quest.type === 'check') {
      //stop video/audio stream
      document.getElementById("progressBar").hidden = true;     //hidden blu progress bar
      window.stopStream();
      document.getElementById("ConfirmTextBtn").hidden = false;
      document.getElementById("video").hidden = true;
      document.getElementById("code").hidden = true;
      document.getElementById("check").hidden = false;
      document.querySelector('button#rec').hidden = true;
      document.getElementById("StartTextBtn").hidden = true;
      document.getElementById("timeBox").hidden = true;
      


      choices_splitted = quest.choices.split(";")
      choices_list_html = ""
      for (var j = 0; j < choices_splitted.length; j++) {
        choices_list_html += '<input type="radio" id="' + j + '" name="gender" value="' + choices_splitted[j] + '"> <label for="' + choices_splitted[j] + '">' + choices_splitted[j] + '</label><br>';
      }
      document.getElementById("check").innerHTML = choices_list_html;
      printRis();

    } else {
      document.getElementById("boxRis").hidden = true;
      console.error("Errore caricamento input risposta");

    }
    window.restart_timer();
  }
  else {
    console.warn("errore caricamento domanda/Domanda terminata");
    window.stopStream();
    document.getElementById("boxRis").hidden = true;
    document.getElementById("questionSection").hidden = true;
    document.getElementById("bfine").hidden = false;
    document.getElementById("colVale").hidden = true;

  }
  function printRis() {
    out = '<a>' + quest.action + '</a><br>';
    titleOut = 'Domanda ' + i ;
    console.log(quest);
    i++;

    document.getElementById("question").innerHTML = out;
    document.getElementById("title").innerHTML = titleOut;
  }

}

function showSpinner(){
  document.getElementById("spinner").hidden = false;
  document.getElementById("boxRis").hidden = true;
}

function hideSpinner(){
  document.getElementById("spinner").hidden = true
  document.getElementById("boxRis").hidden = false;
}

