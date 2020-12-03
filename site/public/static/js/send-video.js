
var formData = new FormData();

prepareSubmit = function(file){
  formData.append('file', file);
  console.log('>> formData >> ', formData);
}

submitFile = function() {
  axios.post('/next/',
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    ).then(function () {
      console.log('SUCCESS!!');
    })
    .catch((error) => {
      if(error.response.status == 503){
        location.replace("https://itcinterview.it/keep_in_touch/")
      }
      console.log('FAILURE!!');
    });
}