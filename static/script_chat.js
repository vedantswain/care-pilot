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
  }
  if (msgClass === "emo"){
    article.classList.add('message', 'is-primary', 'msg-primary');
  }
  const div = document.createElement('div');
  div.classList.add('message-body');
  div.textContent = messageText;
  article.appendChild(div);
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

        var infoMessage = createMessageElement(data.support_info, "info")
        supportDiv.appendChild(infoMessage);
        var emoMessage = createMessageElement(data.support_emo, "emo")
        supportDiv.appendChild(emoMessage);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}