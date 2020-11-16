var file;
var firstName;
var lastName;
var eMail;

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
      swal("In bocca al lupo","Inizio intervista...","success")
      .then(() => {
        window.location.reload();});
      console.log('SUCCESS!!');
    })
      .catch( (error) => {
        if(error.response.status == 415){
          swal("Formato del file non valido","Formati supportati: PDF","error")
        }
        console.log(error.response.status);
      });
    
  }, (error) => {
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