var xmlhttp = new XMLHttpRequest();
var url = "http://80.211.116.141/restex/";

xmlhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
    var quest = JSON.parse(this.responseText);
    getQuestion(quest);
  }
};
xmlhttp.open("GET", url, true);
xmlhttp.send();

function getQuestion(quest) {
  var out = ''
  var i;
  for(i = 0; i < quest.length; i++) {
    out += '<a>' + quest[i].question_text + '</a><br>';
  }
  document.getElementById("id01").innerHTML = out;
}