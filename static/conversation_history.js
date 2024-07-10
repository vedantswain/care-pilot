function chatBubbles(message, sender) {
    const bubble = document.createElement('div');
    bubble.className = sender === 'client' ? 'msg-outgoing' : 'msg-incoming';
    bubble.innerHTML = `<article class="message is-dark"><div class="message-body">${message}</div></article>`;
    document.getElementById('chatWindow').appendChild(bubble);
}

function getHistory(session_id) {
    fetch(`/history/${session_id}`)
    .then(response => response.json())
    .then(data => {
        if (data.chat_history) {
            data.chat_history.forEach(chat => {
                chatBubbles(chat.message, chat.sender);
            });
        } else {
            console.error('No chat history found');
            alert('No chat history found');
        }
    })
    .catch(error => {
        console.error('Error fetching chat history:', error);
        alert('Error fetching chat history');
    });
}

window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    console.log("URL Params Session ID:", sessionId);  // 调试输出
    if (sessionId) {
        getHistory(sessionId);
    } else {
        console.error('Session ID is missing in URL parameters');
        alert('Session ID is missing in URL parameters');
    }
}
