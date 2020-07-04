function setlang(lang, no_reload) {
  var clang = getlang();
  var now = new Date();
  now.setTime(now.getTime() + 365 * 24 * 60 * 60 * 1000);
  document.cookie = "lang=" + lang + ";expires=" + now.toGMTString() + ";path=/";
  if (!no_reload && clang != lang) location.reload();
}

function getlang() {
  var name = "lang=";
  var decoded = decodeURIComponent(document.cookie);
  var ca = decoded.split(";");
  for (var c of ca) {
    while (c.charAt(0) == " ") c = c.substring(1);
    if (c.indexOf(name) == 0) {
      return c.substring(name.length);
    }
  }
}

function getelem(id) {
  return document.getElementById(id);
}

function hide(element) {
  element.hidden = true;
  element.classList.add("hide");
}

function show(element) {
  element.hidden = false;
  element.classList.remove("hide");
}

function activate_delete(ident) {
  hide(getelem("open" + ident));
  show(getelem("confirm" + ident));
  show(getelem("close" + ident));
}

function deactivate_delete(ident) {
  show(getelem("open" + ident));
  hide(getelem("confirm" + ident));
  hide(getelem("close" + ident));
}

$(document).ready(function() {
  M.AutoInit();
  setlang(getlang() || "EN", true);
  $(".dropdown-trigger").dropdown({
    hover: false,
    coverTrigger: false
  });
});