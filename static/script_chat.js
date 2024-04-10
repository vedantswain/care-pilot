let userQueue = JSON.parse(localStorage.getItem('userQueue')) || [
    { id: 1, name: "User1", product: "Pizza" , grateful: 0, ranting: 0, expression:0 },
    { id: 2, name: "User2", product: "Speaker", grateful: 1, ranting: 0, expression: 1 },
    { id: 3, name: "User3", product: "Book",  grateful: 1, ranting: 1, expression: 1 },
    { id: 4, name: "User4", product: "Cup" , grateful: 0, ranting: 1, expression:0}
];

function resetQueueToInitialState() {
    let initialState = [
        { id: 1, name: "User1", product: "Pizza", grateful: 0, ranting: 0, expression: 0 },
        { id: 2, name: "User2", product: "Speaker", grateful: 1, ranting: 0, expression: 1 },
        { id: 3, name: "User3", product: "Book", grateful: 1, ranting: 1, expression: 1 },
        { id: 4, name: "User4", product: "Cup", grateful: 0, ranting: 1, expression: 0 }
    ];

    userQueue = initialState;

    localStorage.setItem('userQueue', JSON.stringify(initialState));

    updateQueueDisplay();
}

function updateQueueBackend() {
    userQueue.shift();
    localStorage.setItem('userQueue', JSON.stringify(userQueue));
    updateQueueDisplay();
}

function updateQueueDisplay() {
    const queueContainer = document.querySelector('.list');
    queueContainer.innerHTML = '';

    userQueue.forEach(user => {
        const userElement = document.createElement('div');
        userElement.className = 'list-item box';
        userElement.href = `../?product=${user.product}&grateful=${user.grateful}&ranting=${user.ranting}&expression=${user.expression}`;
        userElement.innerHTML = `
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

    if (userQueue.length > 0) {
        const nextUserLink = `../?product=${userQueue[0].product}&grateful=${userQueue[0].grateful}&ranting=${userQueue[0].ranting}&expression=${userQueue[0].expression}`;
        window.location.href = nextUserLink;
    } else {
        console.log("The queue is now empty.");
        resetQueueToInitialState();
        const nextUserLink = `../?product=${userQueue[0].product}&grateful=${userQueue[0].grateful}&ranting=${userQueue[0].ranting}&expression=${userQueue[0].expression}`;
        window.location.href = nextUserLink;
    }
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
    article.classList.add('card-content');

    const body = document.createElement('div');
    body.classList.add('content');
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

    const cardId = `${support_type}-card`;
    const headerId = `${support_type}-header`;
    // const footerId = `${support_type}-footer`;
    let loaderId = support_type+'-loader'
    let loader = createLoader(loaderId)

    let card = document.getElementById(cardId);
    let header = document.getElementById(headerId);
    // let footer = document.getElementById(footerId);

    card = document.createElement('div');
    card.id = cardId;
    card.classList.add('card');
    card.style.marginBottom = "5%";

    header = document.createElement('header');
    header.id = headerId;
    header.classList.add('card-header');

    const headerTitle = document.createElement('p');
    headerTitle.classList.add('card-header-title');
    headerTitle.textContent = support_type.toUpperCase();

    header.appendChild(headerTitle);
    header.appendChild(loader);
    
    card.appendChild(header);
    supportDiv.appendChild(card);



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
            card.appendChild(emoMessage);
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

                const footer = document.createElement('div');
                footer.classList.add('card-footer');

                const footerItem = document.createElement('div');
                footerItem.classList.add('card-footer-item');
                
                const label = document.createElement('label');
                label.setAttribute('for', 'customRange3');
                label.classList.add('form-label');
                label.textContent = 'Rate Response';
                footerItem.appendChild(label);

                const input = document.createElement('input');
                input.setAttribute('type', 'range');
                input.classList.add('form-range');
                input.setAttribute('min', '1');
                input.setAttribute('max', '5');
                input.setAttribute('step', '1');
                input.setAttribute('id', 'customRange3');
                input.style.marginLeft = '5%';
                footerItem.appendChild(input);
                footer.appendChild(footerItem)
                card.appendChild(footer);
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

                const footer = document.createElement('p');
                footer.classList.add('card-footer');
                
                const footerItem = document.createElement('div');
                footerItem.classList.add('card-footer-item');
                
                const label = document.createElement('label');
                label.setAttribute('for', 'customRange3');
                label.classList.add('form-label');
                label.textContent = 'Rate Response';
                footerItem.appendChild(label);

                const input = document.createElement('input');
                input.setAttribute('type', 'range');
                input.classList.add('form-range');
                input.setAttribute('min', '1');
                input.setAttribute('max', '5');
                input.setAttribute('step', '1');
                input.setAttribute('id', 'customRange3');
                input.style.marginLeft = '5%';
                footerItem.appendChild(input);
                footer.appendChild(footerItem)
                card.appendChild(footer);
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

                const footer = document.createElement('p');
                footer.classList.add('card-footer');

                const footerItem = document.createElement('div');
                footerItem.classList.add('card-footer-item');
                
                const label = document.createElement('label');
                label.setAttribute('for', 'customRange3');
                label.classList.add('form-label');
                label.textContent = 'Rate Response';
                footerItem.appendChild(label);

                const input = document.createElement('input');
                input.setAttribute('type', 'range');
                input.classList.add('form-range');
                input.setAttribute('min', '1');
                input.setAttribute('max', '5');
                input.setAttribute('step', '1');
                input.setAttribute('id', 'customRange3');
                input.style.marginLeft = '5%';
                footerItem.appendChild(input);
                footer.appendChild(footerItem);
                card.appendChild(footer);
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
            const modal = document.createElement('div');
            modal.id = 'finishModal';
            modal.style.position = 'fixed';
            modal.style.display = 'flex';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.alignContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.backgroundColor = 'rgba(0,0,0,0.4)';
            modal.classList.add('modal');

            const modalContent = document.createElement('div');
            modalContent.classList.add('modal-content');
            modalContent.style.backgroundColor = 'white'; 
            modalContent.style.padding = '20px';
            modalContent.style.borderRadius = '5px';
            modalContent.style.width = 'fit-content';
            modalContent.style.flexDirection = 'column';
            modalContent.style.justifyItems = 'center';

            const value = document.createElement('p');
            value.innerHTML = "CONVERSATION RESOLVED";
            modalContent.appendChild(value);
            
            const nextButton = document.createElement('button');
            nextButton.innerHTML = "Next";
            nextButton.classList.add('next-button');
            modalContent.appendChild(nextButton);


            modal.appendChild(modalContent);
            document.body.appendChild(modal);

            nextButton.onclick = function() {
                endChatSession();
                modal.style.display = "none";
                document.body.removeChild(modal); 
            };

            modal.style.display = "block";
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