var turn_number = 0;

function updateQueueDisplay(data) {
  const queueContainer = document.querySelector('#client-queue');
  queueContainer.innerHTML = '';

  data.clientQueue.forEach((client) => {
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
                            <br><small class="has-text-weight-semibold">${client.category}</small>
                        </p>
                    </div>
                </div>
            </div>
        `;
    queueContainer.appendChild(clientElement);
  });

  nextButton = document.getElementById('nextButton');
  completeButton = document.getElementById('completeButton');

  if (data.clientQueue.length > 0) {
      nextButton.style.display = 'block';
  }
  if (data.clientQueue.length < 3) {
      completeButton.style.display = 'block';
  }

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
  const userConfirmed = confirm('Do you want to go to the next client?');
  if (userConfirmed) {
    fetch(`/${sessionId}/update-clientQueue`)
      .then((response) => response.json())
      .then((data) => {
        if (data.url) {
          window.location.href = data.url;
        }
      })
      .catch((error) => console.error('Error:', error));
  }
}

function goToHistoryPage(session_id) {
    console.log("Session ID:", session_id);
    if (session_id) {
        window.location.href = `/conversation_history?session_id=${session_id}`;
    } else {
        console.error('Session ID is missing');
        alert('Session ID is missing');
    }
}

function showSurveyModal() {
  const goSurvey = confirm(
    'Do you want to end the conversation and go to survey?'
  );
  if (goSurvey) {
    var modal = document.getElementById('finish-modal');
    modal.classList.add('is-active');
  }
}


function createMessageElement(messageText, msgClass, messageHeader = '') {
  const article = document.createElement('article');

  let body = document.createElement('div');

  if (msgClass === 'out') {
    article.classList.add('message', 'is-dark', 'msg-outgoing');
  }
  if (msgClass === 'in') {
    article.classList.add('message', 'is-warning', 'msg-incoming');
  }

  body.classList.add('message-body');
  body.innerHTML = messageText;
  article.appendChild(body);

  return article;
}


function createSupportPane(messageText, msgClass) {
  const article = document.createElement('div');
  article.classList.add('card-content');

    const body = document.createElement('div');
    innerContent = document.createElement('div');
    innerContent.innerHTML = messageText;

  if (msgClass === 'senti') {
    const span = document.createElement('span');
    span.classList.add('icon', 'is-small');
    const icon = document.createElement('i');

    innerContent.classList.add('sentiment-label');
    switch (messageText) {
      case 'Very Positive':
        innerContent.classList.add('very-positive');
        iconClass = 'fa-face-grin-beam';
        icon.classList.add('fas', iconClass);
        break;
      case 'Positive':
        innerContent.classList.add('positive');
        iconClass = 'fa-face-grin';
        icon.classList.add('fas', iconClass);
        break;
      case 'Slightly Positive':
        innerContent.classList.add('slightly-positive');
        iconClass = 'fa-face-smile';
        icon.classList.add('fas', iconClass);
        break;
      case 'Neutral':
        innerContent.classList.add('neutral');
        iconClass = 'fa-face-meh';
        icon.classList.add('fas', iconClass);
        break;
      case 'Slightly Negative':
        innerContent.classList.add('slightly-negative');
        iconClass = 'fa-frown-open';
        icon.classList.add('fas', iconClass);
        break;
      case 'Negative':
        innerContent.classList.add('negative');
        iconClass = 'fa-frown';
        icon.classList.add('fas', iconClass);
        break;
      case 'Very Negative':
        innerContent.classList.add('very-negative');
        iconClass = 'fa-face-angry';
        icon.classList.add('fas', iconClass);
        break;
    }

    span.appendChild(icon);
    innerContent.appendChild(span);
  }

  body.appendChild(innerContent);

    if (msgClass === "info"){

        article.classList.add('is-info')
    }
    if (msgClass === "emo"){
        article.classList.add('is-emo')
    }
    if (msgClass === "trouble"){
        innerContent.innerHTML = "";
        innerContent.appendChild(messageText);
        article.classList.add('is-trouble')
    }
    //article.appendChild(header);
    article.appendChild(body);

  return article;
}

// Rate Emopane & trouble pane!
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
  sliderKeysValidation = [];
  messageFlagsValidation = ['client_response'];
  // sliderKeysValidation = ["TYPE_EMO_REFRAME-helpful_unhelpful"]   // list of keys to validate
  // allKeysExist = sliderKeysValidation.every(key => Object.keys(inTaskValues).includes(key));

  showEmo = sessionStorage.getItem('show_emo') == '1';
  showInfo = sessionStorage.getItem('show_info') == '1';

  if (showEmo) {
    messageFlagsValidation.push('support_emo_sentiment');
    if (turn_number > 1) {      // only visible after 1st turn
        sliderKeysValidation.push('TYPE_EMO_REFRAME-helpful_unhelpful');
        messageFlagsValidation.push('support_emo_reframe');
    }
  }

  if (showInfo) {
    sliderKeysValidation.push('TYPE_INFO_GUIDE-helpful_unhelpful');
    messageFlagsValidation.push('support_trouble', 'support_info');
  }

  // if (sessionStorage.getItem('show_emo') == 0) {
  //     messageFlagsValidation = ['client_response','support_trouble','support_info']
  // }
  // else{
  //     messageFlagsValidation = ['client_response','support_emo_sentiment','support_emo_reframe','support_trouble','support_info']
  // }
  // allFlagsExist = messageFlagsValidation.every(key => Object.keys(messageFlags).includes(key));

  allKeysExist = sliderKeysValidation.every((key) =>
    Object.keys(inTaskValues).includes(key)
  );
  allFlagsExist = messageFlagsValidation.every((key) =>
    Object.keys(messageFlags).includes(key)
  );

  if (allKeysExist && allFlagsExist) {
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
  input.setAttribute('name', `${support_type}-helpful_unhelpful`);
  input.setAttribute('min', '-2');
  input.setAttribute('max', '2');
  input.setAttribute('value', '0');
  input.setAttribute('step', '1');
  input.style.margin = '0 4px';
  input.style.width = '32em';
  input.style.flex = '1';
  input.addEventListener('input', function () {
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

function createLoader(loaderId = 'info-loader') {
  const loader = document.createElement('span');
  loader.classList.add('loader');
  loader.id = loaderId;
  return loader;
}

function retrieveInfoSupport(message,support_type) {
  const infoDiv = document.getElementById('co-pilot');

  const header = document.createElement('div');
  header.classList.add('card-header');
  const headerTitle = document.createElement('div');
  headerTitle.classList.add('card-header-title');
  headerTitle.textContent = common_strings[support_type].toUpperCase();
  let loader = createLoader();
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
    body: JSON.stringify({ client_reply: message, client_id: clientId }),
  })
    .then((response) => response.json())
    .then((data) => {
      const responseContainer = document.createElement('div');
      responseContainer.style.display = 'flex';
      responseContainer.style.flexDirection = 'row';
      responseContainer.style.justifyContent = 'space-around';
      responseContainer.style.alignItems = 'center';
      data.message.forEach((message) => {
        var infoMessage = createSupportPane(message, 'info');
        responseContainer.appendChild(infoMessage);
      });
      infoDiv.appendChild(responseContainer);
      document.getElementById('info-loader').remove();
      // var infoMessage = createSupportPane(data.message, "info", "Suggested Response")
      // console.log(infoMessage);
      // infoDiv.appendChild(infoMessage);
      // document.getElementById('info-loader').remove();

      updateFlag('support_info');
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

function retrieveEmoSupport(message, support_type) {
  const supportDiv = document.getElementById('supportWindow');

  const cardId = `${support_type}-card`;
  const headerId = `${support_type}-header`;
  // const footerId = `${support_type}-footer`;
  let loaderId = support_type + '-loader';
  let loader = createLoader(loaderId);

  let card = document.getElementById(cardId);
  let header = document.getElementById(headerId);
  // let footer = document.getElementById(footerId);

  card = document.createElement('div');
  card.id = cardId;
  card.classList.add('card');
  card.style.marginBottom = '5%';

  header = document.createElement('header');
  header.id = headerId;
  header.classList.add('card-header');

  const headerTitle = document.createElement('p');
  headerTitle.classList.add('card-header-title');
  headerTitle.textContent = common_strings[support_type].toUpperCase();

  header.appendChild(headerTitle);
  header.appendChild(loader);

  card.appendChild(header);
  supportDiv.appendChild(card);

  const sessionId = window.location.pathname.split('/')[1];
  const clientId = sessionStorage.getItem('client_id');

  if (support_type == 'TYPE_SENTIMENT') {
    fetch(`/${sessionId}/sentiment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ client_reply: message, client_id: clientId }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Add this into html
        document.getElementById(loaderId).remove();
        const sentimentPane = createSupportPane(data.message, 'senti');
        card.appendChild(sentimentPane);
        designHeader(header, 'fa-people-arrows');

        updateFlag('support_emo_sentiment');
      })
      .catch((error) => console.error('Error:', error));
  } else {
    fetch(`/${sessionId}/get-emo-support`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        client_reply: message,
        type: support_type,
        client_id: clientId,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        //            var emoMessage = createSupportPane(data.message, "emo")
        //            card.appendChild(emoMessage);
        // supportDiv.appendChild(emoMessage);
        // supportDiv.scrollTop = supportDiv.scrollHeight;
        document.getElementById(loaderId).remove();

        if (support_type == 'TYPE_EMO_SHOES') {
          const shoesPane = createSupportPane(data.message, 'emo');
          card.appendChild(shoesPane);

          designHeader(header, 'fa-people-arrows');

          footer = createFooter(support_type);
          card.appendChild(footer);
        } else if (support_type == 'TYPE_EMO_REFRAME') {
          const thoughtPane = createSupportPane(data.message.thought, 'emo');
          const reframePane = createSupportPane(data.message.reframe, 'emo');
          card.appendChild(thoughtPane);
          card.appendChild(reframePane);

          designHeader(header, 'fa-spa');

          footer = createFooter(support_type);
          card.appendChild(footer);

          updateFlag('support_emo_reframe');
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function sendTroubleFeedback(support_type) {
  const sessionId = window.location.pathname.split('/')[1];
  const clientId = sessionStorage.getItem('client_id');

  var input = document.getElementById(`${support_type}-feedback`);
  var rate = input.value;
  fetch(`/${sessionId}/store-trouble-feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      rate: rate,
      type: support_type,
      client_id: clientId,
    }),
  })
    .then((response) => response.json())
    .catch((error) => {
      console.error('error:', error);
    });
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
    body: JSON.stringify({
      rate: rate,
      type: support_type,
      client_id: clientId,
    }),
  })
    .then((response) => response.json())
    .catch((error) => {
      console.error('Error:', error);
    });
}

function retrieveTroubleSupport(message, support_type) {
  const troubleDiv = document.getElementById('troubleWindow');

  const header = document.createElement('div');
  header.classList.add('card-header');
  const headerTitle = document.createElement('div');
  headerTitle.classList.add('card-header-title');
  headerTitle.textContent = common_strings[support_type].toUpperCase();
  let loaderId = 'trouble-loader';
  let loader = createLoader(loaderId);
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

            const orderList = document.createElement('ol');

            data.message.forEach((message) => {
                var infoMessage = document.createElement('li');
                infoMessage.textContent = message;
                orderList.appendChild(infoMessage);
            });

            var troubleMessage = createSupportPane(orderList, "trouble")


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

      // support_type == "TYPE_TROUBLE"
      footer = createFooter(support_type);
      troubleDiv.appendChild(footer);

      updateFlag('support_trouble');
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

function processClientResponse(data) {
  turn_number += 1;

  const chatDiv = document.getElementById('chatWindow');
  const typing = document.getElementById('typing');
  var aiMessage = createMessageElement(data.message, 'in');
  chatDiv.appendChild(aiMessage);
  chatDiv.scrollTop = chatDiv.scrollHeight;
  typing.style.display = 'none';

  updateFlag('client_response');

  if (data.show_info == '1') {
    const infoDiv = document.getElementById('co-pilot');
    infoDiv.innerHTML = '';
    retrieveInfoSupport(data.message, "TYPE_INFO_CUE");

    const troubleDiv = document.getElementById('troubleWindow');
    troubleDiv.innerHTML = '';
    retrieveTroubleSupport(data.message, 'TYPE_INFO_GUIDE');
  }

  if (data.show_emo == '1') {
    const supportDiv = document.getElementById('supportWindow');
    supportDiv.innerHTML = '';
    //        retrieveEmoSupport(data.message,TYPE_EMO_THOUGHT);
    //        retrieveEmoSupport(data.message,TYPE_EMO_SHOES);
    retrieveEmoSupport(data.message, 'TYPE_SENTIMENT');

    if (turn_number > 1){
        retrieveEmoSupport(data.message, 'TYPE_EMO_REFRAME');
    }

  }
}


function sendMessage() {
  var input = document.getElementById('messageInput');
  var button = document.getElementById('sendButton');
  var message = input.value;

  console.log(message);
  if (message.trim() === '') return;

  input.value = '';
  input.disabled = true;
  button.disabled = true;
  inTaskValues = {}; // reset all flags
  messageFlags = {}; // reset all flags

  const chatDiv = document.getElementById('chatWindow');
  var userMessage = createMessageElement(message, 'out');
  chatDiv.appendChild(userMessage);
  chatDiv.scrollTop = chatDiv.scrollHeight;
  typing.style.display = 'block';

  // const urlParams = new URLSearchParams(window.location.search);
  // const product = urlParams.get('product');
  const sessionId = window.location.pathname.split('/')[1];
  const clientId = sessionStorage.getItem('client_id');
  const showInfo = sessionStorage.getItem('show_info');
  const showEmo = sessionStorage.getItem('show_emo');

  if (showInfo == '1') {
    sendTroubleFeedback('TYPE_INFO_GUIDE');
  }

  if (showEmo == '1') {
    // retrieveEmoFeedback(TYPE_EMO_THOUGHT);
    // retrieveEmoFeedback(TYPE_EMO_SHOES);
    sendEmoFeedback('TYPE_EMO_REFRAME');
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









