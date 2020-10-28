var id = 0;
var prev_question_id = "";
var textArea = document.getElementById("textArea");
var textTmp;
var vidTmp;
var acc = 0;

function question() {
  document.getElementById("boxRis").hidden = false;
  document.getElementById("start").hidden = true;

  

  id = id + 1;
  if(id == 1){
    axios.get('/next/', {
      params: {
        type: 'base'
      }
    })
      .then(function (response) {
        prev_question_id = response.data.id;
        question_type = response.data.type;
        getQuestion(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });
  }else{

    if(question_type === 'video'){ 
      acc++;
      if(acc < 2) return;
      else acc = 0;
      console.log('Window.text: ' + window.text)
      console.log('Window.formData' + window.formData)
      textTmp = window.text; 
      vidTmp = window.formData;  
    }

    if(question_type === 'code'){
      textTmp = textArea;
      vidTmp = "no_video";
    }

    if(question_type === 'check'){
      textTmp = "Laurea";
      vidTmp = "no_video";
    }
    axios.get('/next/', {
      params: {
         
         question_id : prev_question_id,
         answer_text : textTmp,
         answer_vid : vidTmp
        
      }
    })
      .then(function (response) {
        prev_question_id = response.data.id;
        question_type = response.data.type;
        getQuestion(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}

function getQuestion(quest) {
  var out = ''
  var i = 0;
  var titleOut;

  if (quest.id !== undefined) {

    if (quest.type === 'video') {
      document.querySelector('button#rec').hidden = false;
      document.getElementById("video").hidden = false;
      document.getElementById("code").hidden = true;
      document.getElementById("check").hidden = true;
      document.getElementById("StartTextBtn").hidden = true;
      document.getElementById("ConfirmTextBtn").hidden = true;

      printRis();
    } else if (quest.type === 'code') {
      document.getElementById("video").hidden = true;
      document.getElementById("code").hidden = false;
      document.getElementById("check").hidden = true;
      document.querySelector('button#rec').hidden = true;
      document.getElementById("StartTextBtn").hidden = false;
      document.getElementById("ConfirmTextBtn").hidden = true;
      printRis();
    } else if (quest.type === 'check') {
      document.getElementById("ConfirmTextBtn").hidden = false;
      document.getElementById("video").hidden = true;
      document.getElementById("code").hidden = true;
      document.getElementById("check").hidden = false;
      document.querySelector('button#rec').hidden = true;
      document.getElementById("StartTextBtn").hidden = true;
      choices_splitted = quest.choices.split(";")
      choices_list_html =""
      for(var j = 0; j < choices_splitted.length; j++ ){
        choices_list_html += '<input type="radio" id="'+ choices_splitted[j] + '" name="gender" value="'+ choices_splitted[j] + '"> <label for="'+ choices_splitted[j] + '">'+ choices_splitted[j] + '</label><br>';
      }
      document.getElementById("check").innerHTML = choices_list_html;
      printRis();
    }else {
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
    titleOut = '<h1>' + 'Domanda ' + this.id + '</h1>';
    console.log(quest);
    i++;

    document.getElementById("question").innerHTML = out;
    document.getElementById("title").innerHTML = titleOut;
  }

}
/* function postText() {
  var textArea = document.getElementById("textArea");
  axios.post('http://localhost:3000/textArea', {
    //rejectUnauthorized: false,
    text: textArea.value
  })
    .then((response) => {
      console.log(response);
    }, (error) => {
      console.log(error);
    });
} */