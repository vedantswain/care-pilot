function createChatBubble(message, sender) {
    const bubble = document.createElement('article');
    let body = document.createElement('div');

    if (sender === 'representative') {
    bubble.classList.add('message', 'is-dark', 'msg-outgoing');
    }
    if (sender === 'client') {
    bubble.classList.add('message', 'is-warning', 'msg-incoming');
    }

    body.classList.add('message-body');
    body.innerHTML = message;
    bubble.appendChild(body);

    document.getElementById('chatWindow').appendChild(bubble);
}

function displayClientInfo(clients_info) {
    const clientInfoContainer = document.getElementById('clientInfo');
    clientInfoContainer.innerHTML = ''; 

    clients_info.forEach(client => {
        const clientElement = document.createElement('div');
        clientElement.className = 'client-info box';
        clientElement.innerHTML = `
            <div class="media">
                <div class="media-left">
                    <p>
                        <span class="icon is-large">
                            <i class="fas fa-2x fa-circle-user"></i>
                        </span>
                    </p>
                </div>
                <div class="media-content is-hidden-mobile">
                    <div class="content">
                        <p>
                            <strong>${client.client_name}</strong><br>
                            <small class="has-text-weight-semibold">${client.category}</small>
                        </p>
                    </div>
                </div>
            </div>
        `;
        clientElement.addEventListener('click', () => {
            document.getElementById('chatWindow').innerHTML = '';
            getClientHistory(client.client_id, client.client_name);
        });
        clientInfoContainer.appendChild(clientElement);
    });
}

function getClientHistory(client_id, client_name) {
    var clientNameElement = document.getElementById('client-history-name');
    clientNameElement.innerHTML = client_name
    var clientSubtitleElement = document.getElementById('client-history-subtitle');
    clientSubtitleElement.innerHTML = 'Chat History'

    const sessionId = new URLSearchParams(window.location.search).get('session_id');
    fetch(`/history/${sessionId}/${client_id}/`)
    .then(response => response.json())
    .then(data => {
        if (data.chat_history) {
            data.chat_history.forEach(chat => {
                createChatBubble(chat.message, chat.sender);
            });
        } else {
            alert('No chat history found');
        }
    })
    .catch(error => {
        alert('Error fetching chat history');
    });
}

function getHistory(session_id) {
    fetch(`/history/${session_id}`)
    .then(response => response.json())
    .then(data => {
        if (data.clients_info) {
            displayClientInfo(data.clients_info);
        } else {
            alert('No client info found');
        }
    })
    .catch(error => {
        alert('Error fetching client info');
    });
}

window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
        getHistory(sessionId);
    } else {
        alert('Session ID is missing in URL parameters');
    }
}
