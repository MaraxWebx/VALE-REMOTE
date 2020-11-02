var id = 0;
var prev_question_id = "";
var textTmp;
var vidTmp;
var choice_length;
var acc = 0;
var flag = false;
var i = 1;

function question() {
  document.getElementById("boxRis").hidden = true;
  document.getElementById("start").hidden = true;

  id = id + 1;
  if (id == 1) {
    
    axios.get('/next/', {
      params: {
        type: 'base'
      }
    })
      .then(function (response) {
        document.getElementById("boxRis").hidden = false;
        prev_question_id = response.data.id;
        question_type = response.data.type;
        choice_length = response.data.length;
        getQuestion(response.data);
      })
      .catch(function (error) {
        document.getElementById("spinner").innerHTML = `<div style="text-align:center" class="spinner-border text-light" role="status">
                                                       <span class="sr-only">Loading...</span>
                                                      </div>`;
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
      textTmp = document.getElementById("textArea").value;
      vidTmp = "no_video";
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
        document.getElementById("spinner").innerHTML = `<div style="text-align:center" class="spinner-border text-light" role="status">
                                                       <span class="sr-only">Loading...</span>
                                                      </div>`;
      });
  }
}

function getQuestion(quest) {
  var out = ''
  var titleOut;

  if (quest.id !== undefined) {

    if (quest.type === 'video') {
      //start video/audio stream
      window.startCamera();
      document.querySelector('button#rec').hidden = false;
      document.getElementById("video").hidden = false;
      document.getElementById("code").hidden = true;
      document.getElementById("check").hidden = true;
      document.getElementById("StartTextBtn").hidden = true;
      document.getElementById("ConfirmTextBtn").hidden = true;
      document.getElementById("timeBox").hidden = false;
      printRis();

    } else if (quest.type === 'code') {
      //stop video/audio stream
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
  }
  else {
    console.warn("errore caricamento domanda/Domanda terminata");
    //document.getElementById("boxRis").hidden = true;
    document.getElementById("boxRis").innerHTML = '<h3 style= "color: red; background-color: white">' + 'Domande terminate' + '</h3>';
    document.getElementById("title").innerHTML = '<h1 style="text-align: center">' + 'Fine del questionario' + '</h1>';
    document.getElementById("question").innerHTML = "";

  }
  function printRis() {
    out = '<a>' + quest.action + '</a><br>';
    titleOut = '<h1>' + 'Domanda ' + i + '</h1>';
    console.log(quest);
    i++;

    document.getElementById("question").innerHTML = out;
    document.getElementById("title").innerHTML = titleOut;
  }

}