const indexAtBehavior = 2;
const indexAtPersonality = 4;

TIMEOUT_DURATION = 1000;

var defaultDomains = ["mobile-device", "hotel", "airlines"];

const sentiments = [
    '',              // No Emotion
    'Afraid',        // Fear/Anxiety
    'Angry',         // Anger/Frustration
    'Sad',           // Sadness/Disappointment
    'Ashamed',       // Shame/Guilt
    'Calm',          // Calm/Contentment
    'Confused',      // Confusion/Uncertainty
    'Disgust',       // Disgust/Contempt
    'Tired',         // Fatigue/Exhaustion
    'Apathetic',     // Indifference/Detachment
    'Empathetic',    // Empathy/Understanding
    'Apologetic',    // Apology/Regret
    'Attentive',     // Attention/Focus
    'Bitter',        // Bitterness/Resentment
    'Bullied',       // Bullying/Victimization
    'Careless',      // Carelessness/Neglect
    'Curious',       // Curiosity/Interest
    'Defensive',     // Defensiveness/Guardedness
    'Discomfort',    // Discomfort/Pain
    'Disconnected',  // Disconnection/Isolation
    'Disrespected',  // Disrespect/Offense
    'Distracted',    // Distraction/Inattention
    'Happy',         // Happiness/Positivity
    'Shocked',       // Shock/Surprise
    'Resolute',      // Resolution/Determination
    'Rushed'         // Rushed/Pressured
];
var selectedEmotion = ""

var remainingBehaviors = [];

var domainQuestions = [];
var domainMessagesAI = [];
var domainMessagesHuman = [];

const selectedQuestions = [];
var currentIncidentIndex = 0;


function getDataFromTSV(data) {
    data = data.replace(/\r/g, ""); // Remove carriage returns
    data = data.replace("\"\n", "\""); // Remove newlines within quotes
    data = data.replace(/^\s*[\r\n]/gm, "");    // Remove empty lines

    var lines = data.split("\n");
    var result = [];
    var headers = lines[0].split("\t");

    for (var i = 0; i < headers.length; i++) {
        headers[i] = headers[i].replace(/\n|\r/g, "");
    }

    for (var i = 1; i < lines.length; i++) {
        if (lines[i] === "") {
            continue;
        }

        var obj = {};
        var currentline = lines[i].split("\t");

        for (var j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentline[j];
        }

        result.push(obj);
    }
    return result;
}

function setBehaviorContext(selectedBehavior) {
    var qContainer = document.getElementById("qContainer");

    var header = document.createElement('h2');
    header.classList.add("context-blurb");
    header.textContent = "About the representative:" + selectedBehavior;

    qContainer.prepend(header);

    console.log("Behavior Header and Incident HTML appended to container");
}

function setPersonalityContext(selectedPersonality) {
    var qContainer = document.getElementById("qContainer");

    var header = document.createElement('h2');
    header.classList.add("context-blurb");
    header.textContent = "About the workday:" + selectedPersonality;

    qContainer.prepend(header);

    console.log("Personality Header and Incident HTML appended to container");
}

function createConversationHTML(conversation) {
    const container = document.createElement('div');
    container.className = 'conversation';

    const addMessage = (message, className) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = "message";
        messageDiv.classList.add(className);
        messageDiv.textContent = message;
        container.appendChild(messageDiv);

        const spacer = document.createElement('div');
        spacer.className = 'spacer';
        spacer.innerHTML = '&nbsp;';
        container.appendChild(spacer);
    };

    addMessage(conversation["Initial Complaint"], 'customer');
    addMessage(conversation["Support Agent Response 1"], 'representative');
    addMessage(conversation["Follow-up Complaint 1"], 'customer');
    addMessage(conversation["Support Agent Response 2"], 'representative');
    addMessage(conversation["Follow-up Complaint 2"], 'customer');

    return container;
}


function createQuestionHTML(question_id, source, q_num) {
    const container = document.createElement('div');
    container.classList.add('control', 'content');

    if (source === 'human') {
        question = domainMessagesHuman.find(q => q['_id'] === question_id);
    }
    else if (source === 'ai') {
        question = domainMessagesAI.find(q => q['_id'] === question_id);
    }

    const msg = document.createElement('div');
    msg.className = 'support-msg';
    msg.textContent = question["coworker_empathetic_msg"];
    container.appendChild(msg);


    var items = [
        ["Insincere", "Sincere", 'sincerity'],
        ["Not Compassionate", "Compassionate", 'compassion'],
        ["Cold", "Warm", 'warmth'],
        ["Not Actionable", "Actionable", 'actionable'],
        ["Not Relatable", "Relatable", 'relatability']
    ]

    const table = document.createElement('table');
    table.className = 'table';

    items.forEach((item) => {
        var tr = document.createElement('tr');
        var th = document.createElement('th');
        th.textContent = item[0];
        tr.appendChild(th);

        // create 7 table cells with radio for values from -3 to 3
        for (let i = -3; i <= 3; i++) {
            const td = document.createElement('td');
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.name = item[2]+'_'+q_num;
            radio.value = i;
            radio.setAttribute('data-index', question['_id']);
            radio.setAttribute('data-source', source);
            td.appendChild(radio);
            tr.appendChild(td);
        }

        var th = document.createElement('th');
        th.textContent = item[1];
        tr.appendChild(th);

        table.appendChild(tr);
    });

    container.appendChild(table);

    return container;
}


function displayIncident() {
    var qContainer = document.getElementById("qContainer");
    qContainer.innerHTML = '';

    summativeSubmitBtn = document.getElementById('summativeSubmitBtn');
    summativeSubmitBtn.disabled = false;

    var incidentIndex = currentIncidentIndex;

    var progressBar = document.getElementById('progress-bar');
    progressBar.style.display = 'block';
    var progressLoader = document.getElementById('progress-loader');
    progressLoader.style.display = 'none';

    var incidentData = selectedQuestions[incidentIndex];
    console.log("Incident Data for Block "+incidentIndex+": ", incidentData);
    if (incidentData) {
        var questionID = incidentData['ID'];
        // Find the incident in domainQuestions
        var question = domainQuestions.find(q => q['ID'] === questionID);

        var incidentHTML = createConversationHTML(question);

        // behaviorKnown is true when incidentData contains the key 'context_behav'
        var behaviorKnown = 'context_behav' in incidentData;

        // personalityKnown is true when incidentData contains the key 'context_pers'
        var personalityKnown = 'context_pers' in incidentData;

        if (behaviorKnown) {
            setBehaviorContext(incidentData['context_behav']);
        }
        if (personalityKnown) {
            setPersonalityContext(incidentData['context_pers']);
        }
        qContainer.appendChild(incidentHTML);

        // Create the question prompts
        var qPrompts = document.getElementById("qPrompts");
        qPrompts.innerHTML = '';

        const prompt = document.createElement('div');
        prompt.className = 'prompt';
        prompt.classList.add('control', 'content');
        const h5 = document.createElement('h5');
        h5.textContent = "Select an emotion the representative would feel in this situation:";
        prompt.appendChild(h5);

        // insert a dropdown menu for the emotions
        selectedEmotion = "";
        const select = document.createElement('div');
        select.className = 'select';
        const selectEmotion = document.createElement('select');
        selectEmotion.name = 'dat1';
        selectEmotion.required = true;

        // create an option for each sentiment
        sentiments.forEach((sentiment) => {
            const option = document.createElement('option');
            option.value = sentiment;
            option.textContent = sentiment;
            selectEmotion.appendChild(option);
        });

        // Add an event listener for the 'change' event
        selectEmotion.addEventListener('change', (event) => {
            // Get the selected text
            selectedEmotion = event.target.options[event.target.selectedIndex].text;

            console.log('Selected text:', selectedEmotion);
        });

        select.appendChild(selectEmotion);
        prompt.appendChild(select);

        // insert a line break after the input field
        prompt.appendChild(document.createElement('p'));

        const h6 = document.createElement('h6');
        h6.textContent =  "Evaluate the effectiveness of the message below in helping the representative overcome their feeling:";
        prompt.appendChild(h6);
        qPrompts.appendChild(prompt);

        // Create message scores
        var questionList = []
        questionList.push(createQuestionHTML(incidentData['msg_human_id'], 'human',0));
        questionList.push(createQuestionHTML(incidentData['msg_ai_id'], 'ai',1));
        if ('msg_ai_id_null' in incidentData){
            questionList.push(createQuestionHTML(incidentData['msg_ai_id_null'], 'ai',2));
        }
        // shuffle questionList
        questionList.sort(() => Math.random() - 0.5);

        questionList.forEach((question) => {
            qPrompts.appendChild(question);
        });

    } else {
        console.error("Incident data missing.");
    }
}

function nextIncident() {
    const progressBar = document.getElementById('progress-bar');
    progressBar.value = (currentIncidentIndex + 1) / selectedQuestions.length * 100;

    const progressLoader = document.getElementById('progress-loader');
    progressLoader.style.display = 'block';
    progressBar.style.display = 'none';

    currentIncidentIndex++;

    var qContainer = document.getElementById("qContainer");
    qContainer.innerHTML = '';

    if (currentIncidentIndex < selectedQuestions.length) {
        setTimeout(displayIncident, TIMEOUT_DURATION);
    } else {
        document.getElementById('end-modal').classList.add('is-active');
        document.getElementById('survey-modal').classList.remove('is-active');
    }
}

function createIncidentSet() {
    // Select 2 questions which have behavior context in human messages
    // Randomly select 2 incidents from domainQuestions
    const selectedIndices = new Set();
    var currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 2) {
        const randomIndex = Math.floor(Math.random() * domainQuestions.length);

        // if randomIndex is already in selectedIndices, skip to the next iteration
        if (selectedIndices.has(randomIndex)) {
            continue;
        }

        var incident = domainQuestions[randomIndex]['ID'];

        // Find human message(s) for the selected incident
        const humanMsgs = domainMessagesHuman.filter(q => q['incident_id'] === incident);

        // Filter human messages where context_behav is not null
        const humanMsgsWithContext = humanMsgs.filter(q => q['context_behav']);

        // if humanMsgsWithContext is not empty, add the index to selectedIndices
        if (humanMsgsWithContext.length > 0) {
            console.log("Incident with human behavior context: ", incident);
            selectedIndices.add(randomIndex);
            // Randomly select one human message with context_behav
            const randomHumanIndex = Math.floor(Math.random() * humanMsgsWithContext.length);
            const humanMsg = humanMsgsWithContext[randomHumanIndex];
            const context_behav = humanMsg['context_behav'];

            // Find one AI message for the selected incident and context
            const aiMsg = domainMessagesAI.find(q => q['incident_id'] === incident && q['context_behav'] === context_behav);
            // Find one AI message for the selected incident and context as null
            const aiMsgNull = domainMessagesAI.find(q => q['incident_id'] === incident && !q['context_behav'] && !q['context_pers']);

            var incident_dict = {
                'ID': incident,
                'msg_human_id': humanMsg['_id'],
                'msg_ai_id': aiMsg['_id'],
                'msg_ai_id_null': aiMsgNull['_id'],
                'context_behav': context_behav
            };
            selectedQuestions.push(incident_dict);

            selectedIndices.add(randomIndex);
        }
    }

    // Select 2 questions which have personalitu context in human messages
    // Randomly select 2 incidents from domainQuestions
    currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 2) {
        const randomIndex = Math.floor(Math.random() * domainQuestions.length);

        // if randomIndex is already in selectedIndices, skip to the next iteration
        if (selectedIndices.has(randomIndex)) {
            continue;
        }

        var incident = domainQuestions[randomIndex]['ID'];

        // Find human message(s) for the selected incident
        const humanMsgs = domainMessagesHuman.filter(q => q['incident_id'] === incident);

        // Filter human messages where context_pers is not null
        const humanMsgsWithContext = humanMsgs.filter(q => q['context_pers']);

        // if humanMsgsWithContext is not empty, add the index to selectedIndices
        if (humanMsgsWithContext.length > 0) {
            console.log("Incident with human personality", incident);
            selectedIndices.add(randomIndex);
            // Randomly select one human message with context_behav
            const randomHumanIndex = Math.floor(Math.random() * humanMsgsWithContext.length);
            const humanMsg = humanMsgsWithContext[randomHumanIndex];
            const context_pers = humanMsg['context_pers'];

            // Find one AI message for the selected incident and context
            const aiMsg = domainMessagesAI.find(q => q['incident_id'] === incident && q['context_pers'] === context_pers);
            // Find one AI message for the selected incident and context as null
            const aiMsgNull = domainMessagesAI.find(q => q['incident_id'] === incident && !q['context_behav'] && !q['context_pers']);

            var incident_dict = {
                'ID': incident,
                'msg_human_id': humanMsg['_id'],
                'msg_ai_id': aiMsg['_id'],
                'msg_ai_id_null': aiMsgNull['_id'],
                'context_pers': context_pers
            };
            selectedQuestions.push(incident_dict);

            selectedIndices.add(randomIndex);
        }
    }

    // Select 2 questions which have no context in human messages
    // Randomly select 2 incidents from domainQuestions
    currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 2) {
        const randomIndex = Math.floor(Math.random() * domainQuestions.length);

        // if randomIndex is already in selectedIndices, skip to the next iteration
        if (selectedIndices.has(randomIndex)) {
            continue;
        }

        var incident = domainQuestions[randomIndex]['ID'];

        // Find human message(s) for the selected incident
        const humanMsgs = domainMessagesHuman.filter(q => q['incident_id'] === incident);

        // Filter human messages where context_pers is null and context_behav is null
        const humanMsgsWoContext = humanMsgs.filter(q => !q['context_pers'] && !q['context_behav']);
        if (humanMsgsWoContext.length > 0) {
            console.log("Incident with no context", incident);
            selectedIndices.add(randomIndex);
            // Randomly select one human message with context_behav
            const randomHumanIndex = Math.floor(Math.random() * humanMsgsWoContext.length);
            const humanMsg = humanMsgsWoContext[randomHumanIndex];

            // Find one AI message for the selected incident and context
            const aiMsg = domainMessagesAI.find(q => q['incident_id'] === incident && !q['context_pers'] && !q['context_behav']);

            var incident_dict = {
                'ID': incident,
                'msg_human_id': humanMsg['_id'],
                'msg_ai_id': aiMsg['_id'],
            };
            selectedQuestions.push(incident_dict);

            selectedIndices.add(randomIndex);
        }
    }

    // Shuffle the selected questions
    selectedQuestions.sort(() => Math.random() - 0.5);
    console.log("Selected Questions: ", selectedQuestions);

//    displayIncident();
}

function loadHumanMsgs(domainIds) {

    var url = "/summative/phase2/get-tsv/human_msgs/";

    jQuery.ajax({
        url: url,
        dataType: "text",
        success: function(data) {
            var results = getDataFromTSV(data);

            // Remove ".0" from the incident_id
            results.forEach(q => {
                if (q['incident_id'] && typeof q['incident_id'] === 'string') {
                    q['incident_id'] = q['incident_id'].replace(".0", "");
                }
            });

            // Filter questions by selected domain
            domainMessagesHuman = results.filter(q => domainIds.includes(q['incident_id']));
            console.log("Domain Human Messages: ", domainMessagesHuman);

            // Combine AI and Human messages
            createIncidentSet();
        }
    });
}

function loadAIMsgs(domainIds) {

    var url = "/summative/phase2/get-tsv/ai_msgs/";

    jQuery.ajax({
        url: url,
        dataType: "text",
        success: function(data) {
            var results = getDataFromTSV(data);

            // Rename column "context_behv" to "context_behav"
            results.forEach(q => {
                if (q['context_behv']) {
                    q['context_behav'] = q['context_behv'];
                    delete q['context_behv'];
                }
            });

            // Filter questions by selected domain
            domainMessagesAI = results.filter(q => domainIds.includes(q['incident_id']));
            console.log("Domain AI Messages: ", domainMessagesAI);

            loadHumanMsgs(domainIds);
        }
    });
}

function loadIncidents(domain){

    var randomDomain = domain;
    console.log("Selected Domain: " + randomDomain);

    var url = "/summative/phase2/get-tsv/scenarios/";
    var qContainer = document.getElementById("qContainer");

    jQuery.ajax({
        url: url,
        dataType: "text",
        success: function(data) {
            var results = getDataFromTSV(data);
            console.log("Parsed Results:", results);

            // Filter questions by selected domain
            domainQuestions = results.filter(q => q['Domain'] === randomDomain);
            console.log("Domain Questions: ", domainQuestions);

            // List the IDs of the questions
            var domainIds = domainQuestions.map(q => q['ID']);

            // Define categories
            var categories = ["Service Quality", "Product Issues", "Pricing and Charges", "Policy", "Resolution"];

            loadAIMsgs(domainIds);

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Failed to fetch the TSV file. Status: " + textStatus + ", Error: " + errorThrown);
            console.error("Response Text: " + jqXHR.responseText);
        }
    });
}


function validateAndSubmit(e, formElement) {
    e.preventDefault();

    summativeSubmitBtn = document.getElementById('summativeSubmitBtn');
    summativeSubmitBtn.disabled = true;

    const formData = new FormData(formElement);
    const formValues = {};
    formData.forEach((value, key) => { formValues[key] = value; });

    if (selectedEmotion === "") {
        alert("Please respond to all questions.");
        summativeSubmitBtn.disabled = false;
        return;
    }

    // Check if the all radio questions were answered
    var radioKeysValidation = []
    var form_items = 2
    if ('msg_ai_id_null' in selectedQuestions[currentIncidentIndex]){
        form_items = 3
    }
    for (let i = 0; i < form_items; i++) {
        radioKeysValidation.push('sincerity_'+i);
        radioKeysValidation.push('compassion_'+i);
        radioKeysValidation.push('warmth_'+i);
        radioKeysValidation.push('actionable_'+i);
        radioKeysValidation.push('relatability_'+i);
    }


    allKeysExist = radioKeysValidation.every(key => Object.keys(formValues).includes(key));
    if (!allKeysExist){
        alert("Please respond to all radio button questions.");
        summativeSubmitBtn.disabled = false;
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const prolific_id = urlParams.get('PROLIFIC_PID');

    data = formValues
    data['scenario_num'] = currentIncidentIndex
    data['incident_id'] = selectedQuestions[currentIncidentIndex]['ID']
    data['dat1'] = selectedEmotion

    // Retrieve data-index and data-source from the radio buttons
    const radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach((radio) => {
        if (radio.checked) {
            const prompt_num = radio.name.split('_')[1];
            if (!("msg_"+prompt_num in data)){
                data["msg_"+prompt_num] =radio.getAttribute('data-index');
                data["msg_"+prompt_num+"_src"] = radio.getAttribute('data-source');
            }
        }
    });

    fetch(`/store-summative-scoring/${prolific_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');

            summativeSubmitBtn.disabled = false;
        }
        console.log('Feedback submitted successfully!');
        nextIncident();
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error submitting response. Please try again.');

        summativeSubmitBtn.disabled = false;
    });
}

function initiateNextPart() {
    document.getElementById('transition-modal').classList.remove('is-active');
    document.getElementById('survey-modal').classList.add('is-active');

    setTimeout(displayIncident, TIMEOUT_DURATION);
}


function completeSummative() {
    var completeBtn = document.getElementById('completeBtn');
    completeBtn.disabled = true;

    const urlParams = new URLSearchParams(window.location.search);
    const prolific_id = urlParams.get('PROLIFIC_PID');

    fetch(`/summative/phase1/complete/${prolific_id}/`)
    .then(response => {
        // Check if the request was successful
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Parse the JSON response
        return response.json();
    })
    .then((data) => {
         if (data.url) {
           window.location.href = data.url;
         }
    })
    .catch((error) => {
        console.error('Error:', error)
        completeBtn.disabled = false;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('transition-modal').classList.add('is-active');

    var nextBtn = document.getElementById('summativeNextBtn');
    nextBtn.addEventListener('click', initiateNextPart);

    var randomDomain = defaultDomains[Math.floor(Math.random() * defaultDomains.length)];
    console.log("Random Domain: " + randomDomain);

    loadIncidents(randomDomain);

    const form = document.getElementById('summativePhaseI');
    form.addEventListener('submit', function(e) {
        validateAndSubmit(e, this);
    });

    var completeBtn = document.getElementById('completeBtn');
    completeBtn.addEventListener('click', completeSummative);
});




