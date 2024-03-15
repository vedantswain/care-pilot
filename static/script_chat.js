function createMessageElement(messageText, msgClass, messageHeader='') {
  const article = document.createElement('article');

  let body = document.createElement('div');

  if (msgClass === "out"){
    article.classList.add('message', 'is-dark', 'msg-outgoing');
  }
  if (msgClass === "in"){
    article.classList.add('message', 'is-warning', 'msg-incoming');
  }

  body.classList.add('message-body');
  body.innerHTML = messageText;
  article.appendChild(body);

  return article
}

function createSupportPane(messageText, msgClass, messageHeader=''){
    const article = document.createElement('div');
    article.classList.add('card');
    const header = document.createElement('div');
    header.classList.add('card-header');
    const headerTitle = document.createElement('div');
    headerTitle.classList.add('card-header-title');
    headerTitle.textContent = messageHeader.toUpperCase();
    header.appendChild(headerTitle)

    const body = document.createElement('div');
    body.classList.add('card-content');
    innerContent = document.createElement('pre');
    messageText = marked.parse(messageText);
    innerContent.innerHTML = messageText;
    body.appendChild(innerContent);

    if (msgClass === "info"){
        const button = document.createElement('button');
        button.classList.add('card-header-icon')
        const span = document.createElement('span');
        span.classList.add('icon', 'is-small');
        const icon = document.createElement('i');
        icon.classList.add('fas', 'fa-copy');
        span.appendChild(icon)
        button.appendChild(span)

        header.appendChild(button)

        article.classList.add('is-info')
    }
    if (msgClass === "emo"){
        article.classList.add('is-emo')
    }
    article.appendChild(header);
    article.appendChild(body);

    return article
}

function createLoader(parentId='co-pilot', loaderId='info-loader'){
    const infoDiv = document.getElementById(parentId);

    const loader = document.createElement('span');
    loader.classList.add('loader');
    loader.id = loaderId

    infoDiv.appendChild(loader)

    return loader
}

function retrieveInfoSupport(message){
    let loader = createLoader()
    const infoDiv = document.getElementById('co-pilot');

    fetch('/get-info-support', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message}),
        })
        .then(response => response.json())
        .then(data => {
            var infoMessage = createSupportPane(data.message, "info", "Suggested Response")
            infoDiv.appendChild(infoMessage);
            document.getElementById('info-loader').remove();

        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function retrieveEmoSupport(message, support_type){
    let loaderId = support_type+'-loader'
    let loader = createLoader('supportWindow',loaderId)
    const supportDiv = document.getElementById('supportWindow');

    fetch('/get-emo-support', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message, type: support_type}),
        })
        .then(response => response.json())
        .then(data => {
            var emoMessage = createSupportPane(data.message, "emo", support_type)
            supportDiv.appendChild(emoMessage);
            supportDiv.scrollTop = supportDiv.scrollHeight;
            document.getElementById(loaderId).remove();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function processClientResponse(data){
    const chatDiv = document.getElementById('chatWindow');
    const typing = document.getElementById('typing');
    var aiMessage = createMessageElement(data.message, "in")
    chatDiv.appendChild(aiMessage);
    chatDiv.scrollTop = chatDiv.scrollHeight;
    typing.style.display = 'none';


    const infoDiv = document.getElementById('co-pilot');
    infoDiv.innerHTML = '';
    retrieveInfoSupport(data.message);


    const supportDiv = document.getElementById('supportWindow');
    supportDiv.innerHTML = '';
    retrieveEmoSupport(data.message,'reframe_client');
    retrieveEmoSupport(data.message,'reflect');
}

function sendMessage() {
    var input = document.getElementById('messageInput');
    var message = input.value;
    input.value = '';
    input.disabled = true;

    if(message.trim() === '') return;

    const chatDiv = document.getElementById('chatWindow');
    var userMessage = createMessageElement(message, "out")
    chatDiv.appendChild(userMessage);
    chatDiv.scrollTop = chatDiv.scrollHeight;
    typing.style.display = 'block';

    fetch('/get-reply', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({prompt: message}),
    })
    .then(response => response.json())
    .then(data => {
        processClientResponse(data);
        input.disabled = false;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


// Define a function to execute after the page loads
function fetchFirstMsg() {
    const urlParams = new URLSearchParams(window.location.search);
    const chatDiv = document.getElementById('chatWindow');

    // Make a GET request using fetch
    fetch(`/get-reply?${urlParams}`)
    .then(response => {
        // Check if the request was successful
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Parse the JSON response
        return response.json();
    })
    .then(data => {
        // Process the data returned from the server
        processClientResponse(data);
    })
    .catch(error => {
        // Handle any errors that occur during the request
        console.error('Error fetching data:', error);
    });
}

// Register the fetchData function to be executed after the page loads
window.onload = fetchFirstMsg;