var elements = stripe.elements();

// Set up Stripe.js and Elements to use in checkout form
var style = {
  base: {
    color: "#32325d",
    fontWeight: 500,
    fontFamily: "Inter UI, Open Sans, Segoe UI, sans-serif",
    fontSize: "large",
    fontSmoothing: "antialiased",
  }
};

var card = elements.create("card", { style: style });

card.mount("#card-element");

const displayError = document.getElementById('card-errors');

card.on('change', ({error}) => {
  if (error) {
    displayError.textContent = error.message;
  } else {
    displayError.textContent = '';
  }
});

var form = document.getElementById('payment-form');

var clientSecret = document.getElementById("payment-form").getAttribute("data-secret");

form.addEventListener('submit', function(ev) {
  ev.preventDefault();
  stripe.confirmCardPayment(clientSecret, {
    payment_method: {
      card: card
    }
  }).then(function(result) {
    if (result.error) {
      // Show error to your customer (e.g., insufficient funds)
      displayError.textContent = result.error.message;
    } else {
      // The payment has been processed!
      if (result.paymentIntent.status === 'succeeded') {
        // Show a success message to your customer
        // There's a risk of the customer closing the window before callback
        // execution. Set up a webhook or plugin to listen for the
        // payment_intent.succeeded event that handles any business critical
        // post-payment actions.
        alert("Yeet");
      }
    }
  });
});