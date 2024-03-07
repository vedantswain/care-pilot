function createMessageElement(messageText, msgClass) {
  const article = document.createElement('article');

  if (msgClass === "out"){
    article.classList.add('message', 'is-dark', 'msg-outgoing');
  }
  if (msgClass === "in"){
    article.classList.add('message', 'is-warning', 'msg-incoming');
  }
  if (msgClass === "info"){
    article.classList.add('message', 'is-info', 'msg-info');
    const header = document.createElement('div');
    header.classList.add('message-header');
    header.textContent = msgClass.toUpperCase();
    article.appendChild(header);
  }
  if (msgClass === "emo"){
    article.classList.add('message', 'is-primary', 'msg-primary');
    const header = document.createElement('div');
    header.classList.add('message-header');
    header.textContent = msgClass.toUpperCase();
    article.appendChild(header);
  }
  
  const body = document.createElement('div');
  body.classList.add('message-body');
  body.textContent = messageText;
  article.appendChild(body);
  return article
}

function sendMessage() {
    var input = document.getElementById('messageInput');
    var message = input.value;
    input.value = '';
    const chatDiv = document.getElementById('chatWindow');
    const supportDiv = document.getElementById('supportWindow');
    console.log('Working now')

    const loader = document.getElementById('loader');
    const sloader = document.getElementById('sloader');

    if(message.trim() === '') return;

    var userMessage = createMessageElement(message, "out")
    chatDiv.appendChild(userMessage);
    chatDiv.scrollTop = chatDiv.scrollHeight;
    loader.style.display = 'block';

    fetch('/response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({prompt: message}),
    })
    .then(response => response.json())
    .then(data => {
        var aiMessage = createMessageElement(data.message, "in")
        chatDiv.appendChild(aiMessage);
        chatDiv.scrollTop = chatDiv.scrollHeight;
        loader.style.display = 'none';
        sloader.style.display = 'block';

        var infoMessage = createMessageElement(data.support_info, "info")
        supportDiv.appendChild(infoMessage);
        var emoMessage = createMessageElement(data.support_emo, "emo")
        supportDiv.appendChild(emoMessage);
        supportDiv.scrollTop = supportDiv.scrollHeight;
        sloader.style.display = 'none';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}