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
 
  let formData = new FormData();
   formData.append('file', file);
   console.log('>> formData >> ', formData);
   console.log(file.type);
 
   {

     swal("In bocca al lupo!","","success");
     (async () => {
 
       axios.post('/file/', 
 
         //rejectUnauthorized: false,
        // firstname: firstName,
        // lastname: lastName,
         //email: eMail,
         formData, {
            headers: {
              'Content-Type': 'text/plain'
            }
          }
       )
         .then((response) => {
           console.log(response);
         }, (error) => {
           console.log(error);
         });
 
 
       const response = await axios({
         url: 'file/',
         method: 'get'
       })
       console.log(response);
 
     })()
   }
   document.msform.reset();
   this.files = [];
 }
 
 handleFileUpload = function (){
   file = document.getElementById("file").files[0];
   console.log('>>>> 1st element in files array >>>> ', file);
 
 }
 