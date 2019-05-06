const host = window.location.hostname;
const port = 18080;

function queryParams(params) {
	const params_string = [];
  for (k in params) {
  	params_string.push(encodeURIComponent(k) + '=' + encodeURIComponent(params[k]));
  } 
  return '?' + params_string.join('&');
}

function get(path, callback) {
	let xhr = new XMLHttpRequest();
	let url = "http://" + host + ":" + port + path;
	xhr.open('GET', url, true);
	xhr.onload = function() {
		let doc = JSON.parse(xhr.responseText);
		callback(doc);
	}
	xhr.send();
	//alert(path);
}
