
var formData = new FormData();

prepareSubmit = function(file){
  formData.append('file', file);
  console.log('>> formData >> ', formData);
}

submitFile = function() {
  //file = this.$refs.blob.files[0];
 /*
  formData.append('file', file);
  console.log('>> formData >> ', formData);
*/
   // HTTP POST on server
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