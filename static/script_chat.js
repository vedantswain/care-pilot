let userQueue = [
    { id: 1, name: "User1", product: "Pizza" , grateful: 0, ranting: 0, expression:0 },
    { id: 2, name: "User2", product: "Speaker", grateful: 1, ranting: 0, expression: 1 },
    { id: 3, name: "User3", product: "Book",  grateful: 1, ranting: 1, expression: 1 },
    { id: 4, name: "User4", product: "Cup" , grateful: 0, ranting: 1, expression:0}
];

function updateQueueBackend() {
    userQueue.shift();
    updateQueueDisplay();
}

function updateQueueDisplay() {
    const queueContainer = document.querySelector('.list');
    queueContainer.innerHTML = '';

    // Re-add users from the updated queue to the HTML
    userQueue.forEach(user => {
        const userElement = document.createElement('a');
        userElement.className = 'list-item box';
        userElement.href = `../?product=${user.product}&grateful=${user.grateful}&ranting=${user.ranting}&expression=${user.expression}`;
        userElement.innerHTML = `
            <div class="media">
                <div class="media-left">
                    <figure class="image is-48x48 is-32x32-mobile">
                        <img src="https://via.placeholder.com/150" alt="Image" class="is-rounded">
                    </figure>
                </div>
                <div class="media-content is-hidden-mobile">
                    <div class="content">
                        <p>
                            <strong>${user.name}</strong>
                            <br><small class="has-text-weight-semibold">${user.product}</small>
                        </p>
                    </div>
                </div>
            </div>
        `;
        queueContainer.appendChild(userElement);
    });
}

function endChatSession() {
    updateQueueBackend();
    updateQueueDisplay();
}


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


function createSupportPane(messageText, msgClass){
    const article = document.createElement('div');
    article.classList.add('card');

    const body = document.createElement('div');
    body.classList.add('card-content');
    innerContent = document.createElement('div');
    markedmsgText = marked.parse(messageText);
    innerContent.innerHTML = markedmsgText;
    body.appendChild(innerContent);

    if (msgClass === "info"){
        // let header = body.querySelector('.card-header');
        // if (!header) {
        //     header = document.createElement('div');
        //     header.classList.add('card-header');
        //     body.insertBefore(header, body.firstChild); // Insert at the top
        // }

        // const button = document.createElement('button');
        // button.classList.add('card-header-icon');
        // const span = document.createElement('span');
        // span.classList.add('icon', 'is-small');
        // const icon = document.createElement('i');
        // icon.classList.add('fas', 'fa-copy');
        // span.appendChild(icon);
        // button.appendChild(span);
        // header.appendChild(button);
        // //article.appendChild(header);
        // button.addEventListener('click', () => {
        //     navigator.clipboard.writeText(messageText)
        //         .then(() => {
        //             const textarea = document.getElementById('messageInput');
        //             textarea.value = messageText;
        //         })
        //         .catch(err => {
        //             console.error('Could not copy text: ', err);
        //         });
        // });

        article.classList.add('is-info')
    }
    if (msgClass === "emo"){
        article.classList.add('is-emo')
    }
    if (msgClass === "trouble"){
        article.classList.add('is-trouble')
    }
    //article.appendChild(header);
    article.appendChild(body);

    return article
}

function createLoader(loaderId='info-loader') {
    const loader = document.createElement('span');
    loader.classList.add('loader');
    loader.id = loaderId
    return loader;
}

function retrieveInfoSupport(message){
    const infoDiv = document.getElementById('co-pilot');

    const header = document.createElement('div');
    header.classList.add('card-header');
    const headerTitle = document.createElement('div');
    headerTitle.classList.add('card-header-title');
    headerTitle.textContent = "Ways to Continue the Conversation".toUpperCase();
    let loader = createLoader()
    header.appendChild(headerTitle);
    header.appendChild(loader);
    infoDiv.appendChild(header);

    fetch('/get-info-support', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message}),
        })
        .then(response => response.json())
        .then(data => {
            const responseContainer = document.createElement('div');
            responseContainer.style.display = 'flex';
            responseContainer.style.flexDirection = 'row';
            responseContainer.style.justifyContent = 'space-around';
            responseContainer.style.alignItems = 'center';
            data.message.forEach((message) => {
                var infoMessage = createSupportPane(message, "info");
                responseContainer.appendChild(infoMessage);
            });
            infoDiv.appendChild(responseContainer);
            document.getElementById('info-loader').remove();
            // var infoMessage = createSupportPane(data.message, "info", "Suggested Response")
            // console.log(infoMessage);
            // infoDiv.appendChild(infoMessage);
            // document.getElementById('info-loader').remove();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function retrieveEmoSupport(message, support_type){
    const supportDiv = document.getElementById('supportWindow');

    const headerId = `${support_type}-header`;
    const contentId = `${support_type}-content`;
    const footerId = `${support_type}-footer`;
    let loaderId = support_type+'-loader'
    let loader = createLoader(loaderId)

    let header = document.getElementById(headerId);
    let contentContainer = document.getElementById(contentId);
    let footer = document.getElementById(footerId);

    // If the header doesn't exist, create it and the content container
    if (!header) {
        header = document.createElement('div');
        header.id = headerId;
        header.classList.add('card-header');

        const headerTitle = document.createElement('div');
        headerTitle.classList.add('card-header-title');
        headerTitle.textContent = support_type.toUpperCase();

        header.appendChild(headerTitle);
        header.appendChild(loader);
        supportDiv.appendChild(header);

        contentContainer = document.createElement('div');
        contentContainer.id = contentId;
        contentContainer.classList.add('card-content');
        supportDiv.appendChild(contentContainer);

        footer = document.createElement('div');
        footer.id = footerId;
        footer.classList.add('card-footer');
        
        const label = document.createElement('label');
        label.setAttribute('for', 'customRange3');
        label.classList.add('form-label');
        label.textContent = 'Rate Response';
        footer.appendChild(label);

        const input = document.createElement('input');
        input.setAttribute('type', 'range');
        input.classList.add('form-range');
        input.setAttribute('min', '1');
        input.setAttribute('max', '5');
        input.setAttribute('step', '1');
        input.setAttribute('id', 'customRange3');
        input.style.marginLeft = '5%';
        footer.appendChild(input);
        supportDiv.appendChild(footer);
    }



    fetch('/get-emo-support', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message, type: support_type}),
        })
        .then(response => response.json())
        .then(data => {
            var emoMessage = createSupportPane(data.message, "emo")
            contentContainer.appendChild(emoMessage);
            // supportDiv.appendChild(emoMessage);
            // supportDiv.scrollTop = supportDiv.scrollHeight;
            document.getElementById(loaderId).remove();
            if (support_type == "You might be thinking") {
                const p = document.createElement('p');
                p.classList.add('card-header-icon');
                const span = document.createElement('span');
                span.classList.add('icon', 'is-small');
                const icon = document.createElement('i');
                icon.classList.add('fa-solid', 'fa-lightbulb');
                span.appendChild(icon);
                p.appendChild(span);
                header.appendChild(p);
            }
            else if (support_type == "Put Yourself in the Client's Shoes") {
                const p = document.createElement('p');
                p.classList.add('card-header-icon');
                const span = document.createElement('span');
                span.classList.add('icon', 'is-small');
                const icon = document.createElement('i');
                icon.classList.add('fas', 'fa-people-arrows');
                span.appendChild(icon);
                p.appendChild(span);
                header.appendChild(p);
            }
            else if (support_type == "Be Mindful of Your Emotions") {
                const p = document.createElement('p');
                p.classList.add('card-header-icon');
                const span = document.createElement('span');
                span.classList.add('icon', 'is-small');
                const icon = document.createElement('i');
                icon.classList.add('fas', 'fa-spa');
                span.appendChild(icon);
                p.appendChild(span);
                header.appendChild(p);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function retrieveTroubleSupport(message){
    const troubleDiv = document.getElementById('troubleWindow');

    const header = document.createElement('div');
    header.classList.add('card-header');
    const headerTitle = document.createElement('div');
    headerTitle.classList.add('card-header-title');
    headerTitle.textContent = "Ways to Help Your Customers".toUpperCase();
    let loaderId = 'trouble-loader'
    let loader = createLoader(loaderId)
    header.appendChild(headerTitle);
    header.appendChild(loader);
    troubleDiv.appendChild(header);

    fetch('/get-trouble-support', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message}),
        })
        .then(response => response.json())
        .then(data => {
            var troubleMessage = createSupportPane(data.message, "trouble")
            troubleDiv.appendChild(troubleMessage);
            //troubleDiv.scrollTop = supportDiv.scrollHeight;
            document.getElementById(loaderId).remove();
            const p = document.createElement('p');
            p.classList.add('card-header-icon');
            const span = document.createElement('span');
            span.classList.add('icon', 'is-small');
            const icon = document.createElement('i');
            icon.classList.add('fas', 'fa-circle-info');
            span.appendChild(icon);
            p.appendChild(span);
            header.appendChild(p);
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

    const troubleDiv = document.getElementById('troubleWindow');
    troubleDiv.innerHTML = '';
    retrieveTroubleSupport(data.message);


    const supportDiv = document.getElementById('supportWindow');
    supportDiv.innerHTML = '';
    retrieveEmoSupport(data.message,"You might be thinking");
    retrieveEmoSupport(data.message,"Put Yourself in the Client's Shoes");
    retrieveEmoSupport(data.message,'Be Mindful of Your Emotions');
}

function sendMessage() {
    var input = document.getElementById('messageInput');
    var message = input.value;
    input.value = '';
    input.disabled = true;
    console.log(message)

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
        if(data.message === "FINISH:999") {
            alert("CONVERSATION RESOLVED");
            endChatSession();
            typing.style.display = 'none';
            input.disabled = true;
        } else {
            processClientResponse(data);
            input.disabled = false;
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


// Define a function to execute after the page loads
function fetchFirstMsg() {
    updateQueueDisplay()
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