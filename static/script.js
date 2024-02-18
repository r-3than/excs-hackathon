// Example JavaScript code to handle buy/sell actions using AJAX

// Function to handle buy action
function buyStock(quantity) {
    fetch('/buy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'quantity': quantity })
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with response data (e.g., show success/failure message, update balance/share count)
        console.log(data); // Example: Log response data to console
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to handle sell action
function sellStock(quantity) {
    fetch('/sell', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'quantity': quantity })
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with response data (e.g., show success/failure message, update balance/share count)
        console.log(data); // Example: Log response data to console
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
