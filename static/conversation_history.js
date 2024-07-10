function chatBubbles(message, sender) {
    const bubble = document.createElement('div');
    bubble.className = sender === 'client' ? 'msg-outgoing' : 'msg-incoming';
    bubble.innerHTML = `<article class="message ${sender === 'client' ? 'is-link' : 'is-warning'}"><div class="message-body">${message}</div></article>`;
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
                            <strong>Client Name :${client.client_name}</strong><br>
                            <small class="has-text-weight-semibold">ID: ${client.client_id}</small>
                        </p>
                    </div>
                </div>
            </div>
        `;
        clientElement.addEventListener('click', () => {
            document.getElementById('chatWindow').innerHTML = '';
            getClientHistory(client.client_id);
        });
        clientInfoContainer.appendChild(clientElement);
    });
}

function getClientHistory(client_id) {
    const sessionId = new URLSearchParams(window.location.search).get('session_id');
    fetch(`/history/${sessionId}/${client_id}`)
    .then(response => response.json())
    .then(data => {
        if (data.chat_history) {
            data.chat_history.forEach(chat => {
                chatBubbles(chat.message, chat.sender);
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
