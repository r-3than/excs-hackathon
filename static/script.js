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


function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }


  function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }

