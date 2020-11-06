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
 /*
 if(this.file.type=="file"){
   swal("allegare CV!","", "error");
   document.getElementById("file").focus();
   return false;
  }
  */
 
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
      swal("In bocca al lupo!","","success");
    }, (error) => {
      console.log(error);
    });
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
    

   document.msform.reset();
   this.files = [];
 }
 
 handleFileUpload = function (){
   file = document.getElementById("file").files[0];
   console.log('>>>> 1st element in files array >>>> ', file);
 
 }
 