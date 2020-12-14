var file;
var firstName;
var lastName;
var eMail;

window.onload = () => {
  if(getBrowser() !== 'Chrome'){
    alert("Si prega di utilizzare una versione recente di Google Chrome per il corretto funzionamento dell'applicazione.\nPuoi scaricarlo al seguente link: https://www.google.com/intl/it_it/chrome/");
  }
}

function saveData() {
  firstName = document.msform.firstname.value;
  lastName = document.msform.lastname.value;
  eMail = document.msform.email.value;

  if (firstName === "") {
    swal("Inserire Nome!", "", "error");
    document.msform.firstname.focus();
    return false;
  }

  if (lastName === "") {
    swal("Inserire Cognome!", "", "error");
    document.msform.lastname.focus();
    return false;
  }

  var email_valid = /^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-]{2,})+.)+([a-zA-Z0-9]{2,})+$/;
  if (!email_valid.test(eMail)) {
    swal("Inserire un indirizzo Email corretto!", "", "error");
    document.msform.email.focus();
    return false;
  }

  if (this.file === undefined) {
    swal("Allegare CV!", "", "error");
    document.getElementById("file").focus();
    return false;
  }

  terms();
}

function uploadData() {
  axios.post('/restex/', {
    firstname: firstName,
    lastname: lastName,
    email: eMail,
  }, {
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((response) => {
    console.log('Response:', response);
    let formData = new FormData();
    formData.append('file', file);

    axios.post('/file/',
      formData, {
      headers: {
        'Content-Type': 'application/pdf'
      }
    }
    ).then(function () {
      swal("In bocca al lupo","Inizio intervista...","success")
      .then(() => {
        window.location.reload();});
      console.log('SUCCESS!!');
    }).catch( (error) => {
        if(error.response.status == 503){
          location.replace("https://itcinterview.it/keep_in_touch/")
        }else if(error.response.status == 415){
          swal("Formato del file non valido","Formati supportati: PDF","error")
        }
        console.log(error.response.status);
      });
    
  }).catch( (error) => {
    if(error.response.status == 503){
      location.replace("https://itcinterview.it/keep_in_touch/")
    }
    swal("errore connessione server", "Riprova", "error");
    console.log(error);
  });

  document.msform.reset();
  this.files = [];
}

handleFileUpload = function () {
  file = document.getElementById("file").files[0];
  console.log('>>>> 1st element in files array >>>> ', file);
}

function terms() {
  swal({
    title: "Normativa sulla privacy",
    text: `Proseguendo il colloquio, 
    autorizza il trattamento dei suoi dati personali presenti nel video-colloquio
     e nel curriculum vitae ai sensi dell'art. 13 del Decreto Legislativo 30 giugno 2003, n. 196 
    "Codice in materia di protezione dei dati personali" e dell'art. 13 del GDPR (Regolamento UE 2016/679)`,
    icon: "info",
    buttons: ["Non Accetto", "Accetto"],
    dangerMode: true
  })
    .then((willUpload) => {
      if (willUpload) {
        uploadData();
      } else {
        document.msform.reset();
        this.files = [];
      }
    });
}

function getBrowser() {
  agent = navigator.userAgent;
  agent = agent.toLowerCase();
  switch (true) {
    case agent.indexOf("edge")    > -1: return "Edge";
    case agent.indexOf("edg/")    > -1: return "Chromium based edge";
    case agent.indexOf("opr")     > -1: return "Opera";
    case agent.indexOf("chrome")  > -1: return "Chrome";
    case agent.indexOf("trident") > -1: return "ie";
    case agent.indexOf("firefox") > -1: return "Firefox";
    case agent.indexOf("safari")  > -1: return "Safari";
    default: return "other";
}

  
  /*
	var nVer = navigator.appVersion;
	var nAgt = navigator.userAgent;
	var browserName = navigator.appName;
	var fullVersion = '' + parseFloat(navigator.appVersion);
	var majorVersion = parseInt(navigator.appVersion, 10);
	var nameOffset, verOffset, ix;

	// In Opera, the true version is after "Opera" or after "Version"
	if ((verOffset = nAgt.indexOf("Opera")) != -1) {
		browserName = "Opera";
		fullVersion = nAgt.substring(verOffset + 6);
		if ((verOffset = nAgt.indexOf("Version")) != -1)
			fullVersion = nAgt.substring(verOffset + 8);
	}
	// In MSIE, the true version is after "MSIE" in userAgent
	else if ((verOffset = nAgt.indexOf("MSIE")) != -1) {
		browserName = "Microsoft Internet Explorer";
		fullVersion = nAgt.substring(verOffset + 5);
	}
	// In Chrome, the true version is after "Chrome"
	else if ((verOffset = nAgt.indexOf("Chrome")) != -1) {
		browserName = "Chrome";
		fullVersion = nAgt.substring(verOffset + 7);
	}
	// In Safari, the true version is after "Safari" or after "Version"
	else if ((verOffset = nAgt.indexOf("Safari")) != -1) {
		browserName = "Safari";
		fullVersion = nAgt.substring(verOffset + 7);
		if ((verOffset = nAgt.indexOf("Version")) != -1)
			fullVersion = nAgt.substring(verOffset + 8);
	}
	// In Firefox, the true version is after "Firefox"
	else if ((verOffset = nAgt.indexOf("Firefox")) != -1) {
		browserName = "Firefox";
		fullVersion = nAgt.substring(verOffset + 8);
	}
	// In most other browsers, "name/version" is at the end of userAgent
	else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) <
		(verOffset = nAgt.lastIndexOf('/'))) {
		browserName = nAgt.substring(nameOffset, verOffset);
		fullVersion = nAgt.substring(verOffset + 1);
		if (browserName.toLowerCase() == browserName.toUpperCase()) {
			browserName = navigator.appName;
		}
	}
	// trim the fullVersion string at semicolon/space if present
	if ((ix = fullVersion.indexOf(";")) != -1)
		fullVersion = fullVersion.substring(0, ix);
	if ((ix = fullVersion.indexOf(" ")) != -1)
		fullVersion = fullVersion.substring(0, ix);

	majorVersion = parseInt('' + fullVersion, 10);
	if (isNaN(majorVersion)) {
		fullVersion = '' + parseFloat(navigator.appVersion);
		majorVersion = parseInt(navigator.appVersion, 10);
	}


  return browserName;
  */
}

/*
var file;

function saveData() {
   var firstName = document.msform.firstname.value;
   var lastName = document.msform.lastname.value;
   var eMail = document.msform.email.value;
   
   
 
 console.log("questo -------------", this.file);
 
   if ((firstName == "") || (firstName == "undefined")) {
     swal("Inserire Nome!","", "error");
     document.msform.firstname.focus();
     return false;
 }
 if ((lastName == "") || (lastName == "undefined")) {
     swal("Inserire Cognome!","","error");
     document.msform.lastname.focus();
     return false;
 }
 var email_valid = /^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-]{2,})+.)+([a-zA-Z0-9]{2,})+$/;
 if (!email_valid.test(eMail) || (eMail == "") || (eMail == "undefined")) {
     swal("Inserire un indirizzo Email corretto!","","error");
     document.msform.email.focus();
     return false;
 }

    axios.post('/restex/', { 
      firstname: firstName,
      lastname: lastName,
      email: eMail,
    }, {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    ).then((response) => {
      console.log('Response:', response);
      let formData = new FormData();
      formData.append('file', file);
      
      axios.post('/file/',
      formData, {
        headers: {
          'Content-Type': 'application/pdf'
        }
      }
      ).then(function () {
        console.log('SUCCESS!!');
      })
      .catch(function () {
        console.log('FAILURE!!');
      });
      swal("In bocca al lupo!","","success");
    }, (error) => {
      console.log(error);
    });

    
    

   document.msform.reset();
   this.files = [];
 }
 
 handleFileUpload = function (){
   file = document.getElementById("file").files[0];
   console.log('>>>> 1st element in files array >>>> ', file);
 
 }
 */