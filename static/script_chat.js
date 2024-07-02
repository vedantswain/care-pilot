const TYPE_EMO_THOUGHT = common_strings["TYPE_EMO_THOUGHT"]
const TYPE_EMO_SHOES = common_strings["TYPE_EMO_SHOES"]
const TYPE_EMO_REFRAME = common_strings["TYPE_EMO_REFRAME"]
const TYPE_SENTIMENT = common_strings["TYPE_SENTIMENT"]



function updateQueueDisplay(data) {
    const queueContainer = document.querySelector('#client-queue');
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
                            <br><small class="has-text-weight-semibold">${client.complaint}</small>
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


// secret button that used to jump into next conversation
function confirmNextClient(sessionId) {
    const userConfirmed = confirm("Do you want to go to the next client?");
    if (userConfirmed) {
        fetch(`/${sessionId}/update-clientQueue`)
            .then(response => response.json())
            .then(data => {
                if (data.url) {
                    window.location.href = data.url;
                }
            })
            .catch(error => console.error('Error:', error));
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

// Rate Emopane !
var inTaskValues = {};
var messageFlags = {};

function updateInTask(inTaskName, inTaskAmount) {
    inTaskValues[inTaskName] = inTaskAmount;
    validateInput();
}
function updateFlag(flagName) {
    messageFlags[flagName] = 1;
    validateInput();
}

function validateInput() {
    sliderKeysValidation = ["helpful_unhelpful"]
    allKeysExist = sliderKeysValidation.every(key => Object.keys(inTaskValues).includes(key));

    if (sessionStorage.getItem('show_emo') == 0) {
        allKeysExist = true;    // if emo pane is not visible, then this flag should be true
        messageFlagsValidation = ['client_response','support_trouble','support_info']
    }
    else{
        messageFlagsValidation = ['client_response','support_emo_sentiment','support_emo_reframe','support_trouble','support_info']
    }
    allFlagsExist = messageFlagsValidation.every(key => Object.keys(messageFlags).includes(key));

    if (allKeysExist && allFlagsExist){
        var input = document.getElementById('messageInput');
        var button = document.getElementById('sendButton');
        input.disabled = false;
        button.disabled = false;
    }
}

function createFooter(support_type) {
    const footer = document.createElement('div');
    footer.classList.add('card-footer');

    const footerItem = document.createElement('div');
    footerItem.classList.add('card-footer-item');
    footerItem.style.display = 'flex';
    footerItem.style.alignItems = 'center';
    footerItem.style.justifyContent = 'space-between';

    const sliderContainer = document.createElement('div');
    sliderContainer.classList.add('slider-container');
    sliderContainer.style.display = 'flex';
    sliderContainer.style.alignItems = 'center';
    sliderContainer.style.width = '72%';
    sliderContainer.style.padding = '0 4px';

    const leftLabel = document.createElement('span');
    leftLabel.textContent = 'Helpful';
    leftLabel.style.marginRight = '4px';
    leftLabel.style.width = '4em';
    sliderContainer.appendChild(leftLabel);

    const input = document.createElement('input');
    input.id = `${support_type}-feedback`;
    input.setAttribute('type', 'range');
    input.classList.add('slider');
    input.setAttribute('name','helpful_unhelpful');
    input.setAttribute('min', '-2');
    input.setAttribute('max', '2');
    input.setAttribute('value', '0');
    input.setAttribute('step', '1');
    input.style.margin = '0 4px';
    input.style.width = '32em';
    input.style.flex = '1';
    input.addEventListener('input', function() {
        updateInTask(this.name, this.value);
    });
    sliderContainer.appendChild(input);

    const rightLabel = document.createElement('span');
    rightLabel.textContent = 'Unhelpful';
    rightLabel.style.marginLeft = '4px';
    rightLabel.style.width = '4em';
    sliderContainer.appendChild(rightLabel);

    footerItem.appendChild(sliderContainer);
    footer.appendChild(footerItem);

    return footer;
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


            updateFlag('support_info')
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


            updateFlag('support_emo_sentiment')
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

                updateFlag('support_emo_reframe')
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            });
    }
}

function sendEmoFeedback(support_type) {
    const sessionId = window.location.pathname.split('/')[1];
    const clientId = sessionStorage.getItem('client_id');

    var input = document.getElementById(`${support_type}-feedback`);
    var rate = input.value;
    fetch(`/${sessionId}/store-emo-feedback`, {
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

            updateFlag('support_trouble')
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

    updateFlag('client_response');

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
    var button = document.getElementById('sendButton');
    var message = input.value;
    input.value = '';
    input.disabled = true;
    button.disabled = true;
    inTaskValues = {};  // reset all flags
    messageFlags = {};  // reset all flags

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

    if (showEmo == '1') {
        // retrieveEmoFeedback(TYPE_EMO_THOUGHT);
        // retrieveEmoFeedback(TYPE_EMO_SHOES);
        sendEmoFeedback(TYPE_EMO_REFRAME);
       // retrieveEmoFeedback(TYPE_SENTIMENT);
    }

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
            const modal = document.querySelector('#finish-modal');
            modal.classList.add("is-active");

            typing.style.display = 'none';
            input.disabled = true;
        } else {
            processClientResponse(data);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    }



// Define a function to execute after the page loads
function fetchFirstMsg() {
    var input = document.getElementById('messageInput');
    var button = document.getElementById('sendButton');
    input.disabled = true;
    button.disabled = true;

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









