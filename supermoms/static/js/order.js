var types = [];
var counts = [];

function add(i) {
  if (counts[i] === undefined) counts[i] = 0;
  if (types[i] === undefined) types[i] = parseInt(document.getElementById("counter-" + i).getAttribute("data-product-type"));
  
  if (types[i] != 1 || counts[i] < 1) document.getElementById("counter-" + i).innerHTML = document.getElementById("value-" + i).value = ++counts[i];
  
  update_location_block();
}

function rm(i) {
  if (counts[i] === undefined) counts[i] = 0;
  if (types[i] === undefined) types[i] = parseInt(document.getElementById("counter-" + i).getAttribute("data-product-type"));
  
  if (counts[i] > 0) document.getElementById("counter-" + i).innerHTML = document.getElementById("value-" + i).value = --counts[i];
  
  update_location_block();
}

function update_location_block() {
  for (var x in counts) {
    if (counts[x] > 0 && types[x] === 1) {
      document.getElementById("curb").disabled = true;
      document.getElementById("drop").disabled = true;
      return;
    }
  }
  document.getElementById("curb").disabled = false;
  document.getElementById("drop").disabled = false;
}

window.onload = function() {
  var date = new Date();
  document.getElementById("date").value = date.getFullYear() + "-" + (date.getMonth() + 1).toString().padStart(2, "0") + "-" + date.getDate().toString().padStart(2, "0");
  
  var update = function() {
    var d = document.getElementById("date").value.split("-");
    [...document.getElementById("time").children].forEach(e => { e.hidden = true; if (e.selected) { document.getElementById("time-blank").selected = true; } });
    fetch("/api/available-times/" + d[0] + "/" + d[1] + "/" + d[2]).then(response => response.text()).then(text => JSON.parse(text).forEach(t => document.getElementById("time-" + t).hidden = false));
  }
  
  update();
  
  document.getElementById("date").onchange = update;
}