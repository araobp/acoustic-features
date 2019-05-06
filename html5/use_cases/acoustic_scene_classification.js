app.title = "My home";

const classLabels = {
  0: "chatting",
  1: "reading a book",
  2: "watching TV",
  3: "cocking",
  4: "hamster grinding teeth",
  5: "silence",
  6: "vacuum cleaner",
  7: "showering",
  8: "washing machine",
  9: "doing the dishes",
  10: "walking the room",
  11: "playing the piano",
  12: "going up or down the stairs",
  13: "eating snack"
}
// MQTT topic
const TOPIC = 'sensor';

// Class labels
const numClasses = Object.keys(classLabels).length
const classLabelsName = Object.values(classLabels).reverse();

// Chirt
const NUM_RECORDS = 20;
const INTERVAL = 10;

// Create Chart object
let ctx = document.getElementById('Log').getContext('2d');
let chart = new Chart(ctx, {
  type: 'line',

  data: {
    labels: [],
    datasets: [{
      borderColor: 'rgb(255, 99, 132)',
      data: [],
      fill: false,
      pointStyle: 'rect',
      steppedLine: 'after'
    }]
  },

  options: {
    legend: {
      display: false,
    },
    title: {
      display: true,
      text: 'Acoustic Scene Classification',
      fontSize: 20
    },
    scales: {
      yAxes: [{
        ticks: {
          callback: function(value, index, values) {
            return classLabelsName[index] + '(' + value + ')';
          },
          min: 0,
          max: numClasses - 1,
          stepSize: 1
        }
      }]
    }
  }
});

// Find the most frequent class
function mostFrequent(buf) {
  let win = -1;
  // Frequency of appearance
  Object.keys(buf).forEach(key => {
    if (win == -1) {
      win = key;
    } else if (buf[key] > buf[win]) {
      win = key;
    }
  });
  //console.log(buf);
  return win;
}

// MQTT message serial number
let sno = 0;

// FIFO buffer for logging
let reached = false;

// Buffer for taking an frequency of appearance
let buf = {};

function updateMessage(data) {
  let classLabelInt = parseInt(data);
  let name = classLabels[classLabelInt];
  app.message = name + "(" + data + ")";
}

function updateChart(data, sno) {

  let classLabelInt = parseInt(data);

  // Buffering
  if (classLabelInt in buf) {
    buf[classLabelInt]++;
  } else {
    buf[classLabelInt] = 1;
  }
  if ((sno % INTERVAL) == 0) {
    let win = mostFrequent(buf);
    buf = {};

    // Put in FIFO buffer and update Chart
    chart.data.datasets[0].data.push(win);
    chart.data.labels.push(date_time.toLocaleTimeString());
    if (!reached && chart.data.datasets[0].data.length > NUM_RECORDS) {
      reached = true;
    }
    else if (reached) {
      chart.data.datasets[0].data.shift();
      chart.data.labels.shift();
    }
    chart.update();
  }

}

// Called when MQTT message has arrived 
function onMessageArrived(msg) {

  let data = msg.payloadString;
  //console.log(data);
  data = data.split(',')
  let device_name = data[0];
  if (device_name == app.device_name) {

    let epoch_time = parseFloat(data[1]) * 1000;  // milliseconds
    let date_time = new Date(epoch_time);
    app.timestamp = date_time;
    sno = sno + 1;
    app.sno = sno;

    let payload = data[2];
    updateMessage(payload);
    updateChart(payload, sno);
  }
}


// Called when connected to MQTT server
function onConnect() {
  console.log('Connected to MQTT server');
  mqtt.subscribe(TOPIC);
}

// Connect to MQTT server
function connect() {
  const host = window.location.hostname
  const port = 11883  // MQTT over WebSocket
  mqtt = new Paho.MQTT.Client(host, port, uuidv4());

  let options = {
    timeout: 3,
    onSuccess: onConnect,
  };
  mqtt.onMessageArrived = onMessageArrived
  mqtt.connect(options);
  console.log('Connecting to MQTT server: ' + host)
}

// Called when one of the radio buttons is checked
function onButtonChecked() {
  let form = document.getElementById("select");
  let current = document.getElementById("current");
  let past = document.getElementById("past");
  if (form.operation.value == "current") {
    mqtt.subscribe(TOPIC);
    current.style.display = "block";
    past.style.display = "none";
    chart.data.datasets[0].data = [];
    chart.data.labels = [];
    chart.update();
  } else if (form.operation.value == "past") {
    mqtt.unsubscribe(TOPIC);
    current.style.display = "none";
    past.style.display = "block";
    // Set default datetime
    let tzoffset = (new Date()).getTimezoneOffset() * 60000;
    let now = (new Date(Date.now() - tzoffset)).toISOString().slice(0, 16);
    document.querySelector('input[name="from"]').value = now;
    document.querySelector('input[name="to"]').value = now;
  }
}

// Called when date and time is entered 
function onDateTimeEntered() {
  let from = document.querySelector('input[name="from"]');
  let to = document.querySelector('input[name="to"]');
  from = new Date(from.value).getTime()/1000.0;  // Epoch time in seconds
  to = new Date(to.value).getTime()/1000.0;  // Epoch time in seconds

  get('/log/' + app.device_name + queryParams({from: from, to: to}), doc => {
    //console.log(doc);
    // Update chart
    let data = [];
    let labels = [];
    let localeTime;
    let cnt = 0;
    let buf = {};
    doc.forEach(it => {
      let classLabelInt = parseInt(it.data);
      if (classLabelInt in buf) {
        buf[classLabelInt]++;
      } else {
        buf[classLabelInt] = 1;
      }
      if ((++cnt % INTERVAL) == 0) {
        let win = mostFrequent(buf);
        data.push(win);
        localeTime = parseFloat(it.timestamp) * 1000;
        localeTime = new Date(localeTime).toLocaleTimeString();
        labels.push(localeTime);
        buf = {};
      }
    })
    //console.log(data, labels);
    chart.data.datasets[0].data = data;
    chart.data.labels = labels;
    chart.update();
  });

  return false;
}

// Initiate a connection to MQTT server
connect();
