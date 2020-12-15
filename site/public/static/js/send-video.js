
var formData = new FormData();

prepareSubmit = function(file){
  formData.append('file', file);
  console.log('>> formData >> ', formData);
}

submitFile = function() {
  flag_sub = false;
  axios.post('/next/',
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    ).then(function () {
      flag_sub = true;
    })
    .catch((error) => {
      if(error.response.status == 503){
        location.replace("https://itcinterview.it/keep_in_touch/")
      }
    });
    return flag_sub;
}