let formData = new FormData();

submitFile = function(file) {
  //file = this.$refs.blob.files[0];
 
  formData.append('file', file);
  console.log('>> formData >> ', formData.values);

  /* // HTTP POST on server
  axios.post('http://80.211.116.141/upload_video/',
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
    }); */
}