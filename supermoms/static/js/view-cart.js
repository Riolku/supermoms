function form_submit(val) {
  $("form_pay_method").value = val;
  
  $("form").submit()
}

$("#paypal").onclick(e => {
  form_submit("paypal");
});

$("#paycard").onclick(e => {
  form_submit("card");
});