const TYPE_EMO_THOUGHT = "You might be thinking";
const TYPE_EMO_SHOES = "Put Yourself in the Client's Shoes"
const TYPE_EMO_REFRAME = "Be Mindful of Your Emotions";
const TYPE_SENTIMENT = "Client's Sentiment";

// let userQueue = JSON.parse(localStorage.getItem('userQueue')) || [
//     { id: 1, name: "User1", product: "Pizza" , grateful: 0, ranting: 0, expression:0, civil: 1, info: 1, emo: 1},
//     { id: 2, name: "User2", product: "Speaker", grateful: 1, ranting: 0, expression: 1, civil: 1, info: 1, emo: 0},
//     { id: 3, name: "User3", product: "Book",  grateful: 1, ranting: 1, expression: 1, civil: 0, info: 0, emo: 1},
//     { id: 4, name: "User4", product: "Cup" , grateful: 0, ranting: 1, expression:0, civil: 0, info: 0, emo: 0}
// ];

// function resetQueueToInitialState() {
//     let initialState = [
//         { id: 1, name: "User1", product: "Pizza" , grateful: 0, ranting: 0, expression:0, civil: 1 , info: 1, emo: 1},
//         { id: 2, name: "User2", product: "Speaker", grateful: 1, ranting: 0, expression: 1, civil: 1 , info: 1, emo: 0},
//         { id: 3, name: "User3", product: "Book",  grateful: 1, ranting: 1, expression: 1, civil: 0 , info: 0, emo: 1},
//         { id: 4, name: "User4", product: "Cup" , grateful: 0, ranting: 1, expression:0, civil: 1 , info: 1, emo: 1}
//     ];

//     userQueue = initialState;

//     localStorage.setItem('userQueue', JSON.stringify(initialState));

//     updateQueueDisplay();
// }

// function updateQueueBackend() {
//     userQueue.shift();
//     localStorage.setItem('userQueue', JSON.stringify(userQueue));
//     updateQueueDisplay();
// }

function updateQueueDisplay(data) {
    const queueContainer = document.querySelector('.list');
    queueContainer.innerHTML = '';

    data.clientQueue.forEach(client => {
        const clientElement = document.createElement('div');
        clientElement.className = 'list-item box';
        // userElement.href = `../?product=${user.product}&grateful=${user.grateful}&ranting=${user.ranting}&expression=${user.expression}&civil=${user.civil}&info=${user.info}&emo=${user.emo}`;
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
                            <strong>${client.name}</strong>
                            <br><small class="has-text-weight-semibold">${client.product}</small>
                        </p>
                    </div>
                </div>
            </div>
        `;
        queueContainer.appendChild(clientElement);
    });
}

// function endChatSession() {
 

//     if (userQueue.length > 0) {
        // const nextUserLink = `../?product=${userQueue[0].product}&grateful=${userQueue[0].grateful}&ranting=${userQueue[0].ranting}&expression=${userQueue[0].expression}&civil=${userQueue[0].civil}&info=${userQueue[0].info}&emo=${userQueue[0].emo}`;
        // window.location.href = nextUserLink;
//     } else {
//         console.log("The queue is now empty.");
//         resetQueueToInitialState();
//         const nextUserLink = `../?product=${userQueue[0].product}&grateful=${userQueue[0].grateful}&ranting=${userQueue[0].ranting}&expression=${userQueue[0].expression}&civil=${userQueue[0].civil}&info=${userQueue[0].info}&emo=${userQueue[0].emo}`;
//         window.location.href = nextUserLink;
//     }
// }


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
    innerContent = document.createElement('div');
    markedmsgText = marked.parse(messageText);
    innerContent.innerHTML = markedmsgText;

    if (msgClass === "senti"){
        const span = document.createElement('span');
        span.classList.add('icon', 'is-small');
        const icon = document.createElement('i');

        innerContent.classList.add('sentiment-label')
        switch (messageText) {
            case 'Very Positive':
              innerContent.classList.add('very-positive');
              iconClass = 'fa-face-grin-beam'
              icon.classList.add('fas', iconClass);
              break;
            case 'Positive':
              innerContent.classList.add('positive');
              iconClass = 'fa-face-grin'
              icon.classList.add('fas', iconClass);
              break;
            case 'Slightly Positive':
              innerContent.classList.add('slightly-positive');
              iconClass = 'fa-face-smile'
              icon.classList.add('fas', iconClass);
              break;
            case 'Neutral':
              innerContent.classList.add('neutral');
              iconClass = 'fa-face-meh'
              icon.classList.add('fas', iconClass);
              break;
            case 'Slightly Negative':
              innerContent.classList.add('slightly-negative');
              iconClass = 'fa-frown-open'
              icon.classList.add('fas', iconClass);
              break;
            case 'Negative':
              innerContent.classList.add('negative');
              iconClass = 'fa-frown'
              icon.classList.add('fas', iconClass);
              break;
            case 'Very Negative':
              innerContent.classList.add('very-negative');
              iconClass = 'fa-face-angry'
              icon.classList.add('fas', iconClass);
              break;
          }


        span.appendChild(icon);
        innerContent.appendChild(span);
    }

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

function createFooter(support_type){
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
    input.id = `${support_type}-feedback`;
    input.setAttribute('type', 'range');
    input.classList.add('form-range');
    input.setAttribute('min', '1');
    input.setAttribute('max', '5');
    input.setAttribute('step', '1');
    input.style.marginLeft = '5%';
    footerItem.appendChild(input);
    footer.appendChild(footerItem)

    return footer
}

function designHeader(header, iconClass) {
    const p = document.createElement('p');
    p.classList.add('card-header-icon');
    const span = document.createElement('span');
    span.classList.add('icon', 'is-small');
    const icon = document.createElement('i');
    icon.classList.add('fas', iconClass);
    span.appendChild(icon);
    p.appendChild(span);
    header.appendChild(p);
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

    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');

    fetch(`/${sessionId}/get-info-support`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message, client_id: clientId}),
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

    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');

    if (support_type == TYPE_SENTIMENT) {
        fetch(`/${sessionId}/sentiment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ client_reply: message, client_id: clientId }),
        })
        .then(response => response.json())
        .then(data => {
            // Add this into html
            document.getElementById(loaderId).remove();
            const sentimentPane = createSupportPane(data.message, "senti");
            card.appendChild(sentimentPane);
            designHeader(header, 'fa-people-arrows');
        })
        .catch(error => console.error('Error:', error));
    }
    else {
        fetch(`/${sessionId}/get-emo-support`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message, type: support_type, client_id: clientId}),
        })
        .then(response => response.json())
        .then(data => {
//            var emoMessage = createSupportPane(data.message, "emo")
//            card.appendChild(emoMessage);
            // supportDiv.appendChild(emoMessage);
            // supportDiv.scrollTop = supportDiv.scrollHeight;
            document.getElementById(loaderId).remove();

        if (support_type == TYPE_EMO_SHOES) {
                const shoesPane = createSupportPane(data.message, "emo");
                card.appendChild(shoesPane);

                designHeader(header, 'fa-people-arrows');

                footer = createFooter(support_type)
                card.appendChild(footer);
            }
        else if (support_type == TYPE_EMO_REFRAME) {
            const thoughtPane = createSupportPane(data.message.thought, "emo");
            const reframePane = createSupportPane(data.message.reframe, "emo");
            card.appendChild(thoughtPane);
            card.appendChild(reframePane);

            designHeader(header, 'fa-spa');

            footer = createFooter(support_type);
            card.appendChild(footer);
        }
        })
        .catch((error) => {
            console.error('Error:', error);
            });
    }
}


function retrieveEmoFeedback(support_type) {
    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');

    var input = document.getElementById(`${support_type}-feedback`);
    var rate = input.value;
    fetch(`/${sessionId}/get-emo-feedback`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({rate: rate, type: support_type, client_id: clientId}),
    })
    .then(response => response.json())
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
    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');

    fetch(`/${sessionId}/get-trouble-support`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({client_reply: message, client_id: clientId}),
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

function updateClientQueue() {
    const sessionId = window.location.pathname.split('/')[1];

    fetch(`/${sessionId}/update-clientQueue`)
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            window.location.href = data.url;
        }
    })
    .catch(error => console.error('Error updating client queue:', error));
}

function processClientResponse(data){
    const chatDiv = document.getElementById('chatWindow');
    const typing = document.getElementById('typing');
    var aiMessage = createMessageElement(data.message, "in")
    chatDiv.appendChild(aiMessage);
    chatDiv.scrollTop = chatDiv.scrollHeight;
    typing.style.display = 'none';

    if (data.show_info == '1') {
        const infoDiv = document.getElementById('co-pilot');
        infoDiv.innerHTML = '';
        retrieveInfoSupport(data.message);

        const troubleDiv = document.getElementById('troubleWindow');
        troubleDiv.innerHTML = '';
        retrieveTroubleSupport(data.message);
    }

    if (data.show_emo == '1') {
        const supportDiv = document.getElementById('supportWindow');
        supportDiv.innerHTML = '';
//        retrieveEmoSupport(data.message,TYPE_EMO_THOUGHT);
//        retrieveEmoSupport(data.message,TYPE_EMO_SHOES);
        retrieveEmoSupport(data.message, TYPE_SENTIMENT);
        retrieveEmoSupport(data.message,TYPE_EMO_REFRAME);
    }
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

    // const urlParams = new URLSearchParams(window.location.search);
    // const product = urlParams.get('product');
    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');
    const showInfo = sessionStorage.getItem('show_info');
    const showEmo = sessionStorage.getItem('show_emo');

    fetch(`/${sessionId}/get-reply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({prompt: message, client_id: clientId, show_info: showInfo, show_emo: showEmo}),
    })
    .then(response => response.json())
    .then(data => {
        const isFinish = data.message.includes("FINISH:999");
        if(isFinish) {
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
                //update pop userQueue  from flask backend
                updateClientQueue()
                modal.style.display = "none";
                document.body.removeChild(modal); 
            };

            modal.style.display = "block";
            typing.style.display = 'none';
            input.disabled = true;
        } else {
            if (showEmo == '1') {
                // retrieveEmoFeedback(TYPE_EMO_THOUGHT);
                // retrieveEmoFeedback(TYPE_EMO_SHOES);

                retrieveEmoFeedback(TYPE_EMO_REFRAME);
//                retrieveEmoFeedback(TYPE_SENTIMENT);
            }
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
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = window.location.pathname.split('/')[1];

    // Make a GET request using fetch
    fetch(`/${sessionId}/get-reply?${urlParams}`)
    .then(response => {
        // Check if the request was successful
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Parse the JSON response
        return response.json();
    })
    .then(data => {
        sessionStorage.setItem("client_id", data.client);
        sessionStorage.setItem("show_info", data.show_info);
        sessionStorage.setItem("show_emo", data.show_emo);
        updateQueueDisplay(data);
        processClientResponse(data);
    })
    .catch(error => {
        // Handle any errors that occur during the request
        console.error('Error fetching data:', error);
    });
}

// Register the fetchData function to be executed after the page loads
window.onload = fetchFirstMsg;