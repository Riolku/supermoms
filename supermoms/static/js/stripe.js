var client_id = document.getElementById("payment-form").getAttribute("data-id");

var stripe = Stripe(client_id);