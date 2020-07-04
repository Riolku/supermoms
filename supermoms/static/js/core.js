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

function activate_delete(ident) {
  $("#open" + ident).hide();
  $("#confirm" + ident).show();
  $("#close" + ident).show();
}

function deactivate_delete(ident) {
  $("#open" + ident).show();
  $("#confirm" + ident).hide();
  $("#close" + ident).hide();
}

$(document).ready(function() {
  M.AutoInit();
  setlang(getlang() || "EN", true);
  $(".dropdown-trigger").dropdown({
    hover: false,
    coverTrigger: false
  });
});