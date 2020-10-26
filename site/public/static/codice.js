var app = new Vue({
  el: "#app",
  data: {
    file: ''
  },
  methods: {
    submitFile() {
      let formData = new FormData();
      formData.append('file', this.file);
      console.log('>> formData >> ', formData);

      // You should have a server side REST API 
      axios.post('/upload_video/',
          formData
        ).then(function () {
          console.log('SUCCESS!!');
        })
        .catch(function () {
          console.log('FAILURE!!');
        });
    },
    handleFileUpload() {
      this.file = this.$refs.file.files[0];
      console.log('>>>> 1st element in files array >>>> ', this.file);
    }
  }
});
