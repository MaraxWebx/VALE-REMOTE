
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
    .catch(function () {
      console.log('FAILURE!!');
    });
}