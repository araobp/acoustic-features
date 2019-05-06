// Initialize the device list
get('/devices', devices => {
  let select = document.getElementById("devices");
  devices.forEach(it => {
    select.options[select.options.length] = new Option(it);
  });
});

// Vue component
let app = new Vue({
  el: '#app',
  data: {
    title: '',
    device_name: '',
    timestamp: '',
    message: '',
    sno: 0  // Serial number
  }
});
