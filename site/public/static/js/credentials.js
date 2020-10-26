function emailIsValid(email = document.getElementById("email").value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};


function saveData() {
  var firstName = document.getElementById("firstname");
  var lastName = document.getElementById("lastname");
  var email = document.getElementById("email");




  if (emailIsValid(email.value)) {
    alert(`
               Nome: ${firstName.value} 
               Cognome: ${lastName.value} 
               Email: ${email.value}`);


    (async () => {

      axios.post('/restex/', {
        //rejectUnauthorized: false,
        firstname: firstName.value,
        lastname: lastName.value,
        email: email.value
      })
        .then((response) => {
          console.log(response);
        }, (error) => {
          console.log(error);
        });


      const response = await axios({
        url: '/restex/',
        method: 'get'
      })
      console.log(response);

    })()
  }
}

