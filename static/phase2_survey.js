const indexAtBehavior = 2;
const indexAtPersonality = 4;

TIMEOUT_DURATION = 1000;

var defaultDomains = ["mobile-device", "hotel", "airlines"];


var remainingBehaviors = [];

var domainQuestions = [];
var domainMessagesAI = [];
var domainMessagesHuman = [];

const selectedQuestions = [];
var currentIncidentIndex = 0;


function getDataFromTSV(data) {
    data = data.replace(/\r/g, ""); // Remove carriage returns
    data = data.replace("\"\n", "\""); // Remove newlines within quotes

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
    header.textContent = "" + selectedBehavior;

    qContainer.prepend(header);

    console.log("Behavior Header and Incident HTML appended to container");
}

function setPersonalityContext(selectedPersonality) {
    var qContainer = document.getElementById("qContainer");

    var header = document.createElement('h2');
    header.classList.add("context-blurb");
    header.textContent = selectedPersonality;

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

function displayIncident() {
    var qContainer = document.getElementById("qContainer");

    var qContainer = document.getElementById("qContainer");
    qContainer.innerHTML = '';
    document.querySelector('input[name="dat1"]').value = "";

    document.querySelector('input[name="dat1"]').disabled = false;

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

    document.querySelector('input[name="dat1"]').disabled = true;

    if (currentIncidentIndex < selectedQuestions.length) {
        if (currentIncidentIndex === indexAtBehavior || currentIncidentIndex === indexAtPersonality) {
            setTimeout(initiateTransition, TIMEOUT_DURATION);
        }
        else {
            setTimeout(displayIncident, TIMEOUT_DURATION);
        }
    } else {
        document.getElementById('end-modal').classList.add('is-active');
        document.getElementById('survey-modal').classList.remove('is-active');
    }
}

function createIncidentSet() {
    // Select 3 questions which have behavior context in human messages
    // Randomly select 3 incidents from domainQuestions
    const selectedIndices = new Set();
    var currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 3) {
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
            console.log("Incident with huma behavior context: ", incident);
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

    // Select 3 questions which have personalitu context in human messages
    // Randomly select 3 incidents from domainQuestions
    currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 3) {
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

    // Select 4 questions which have no context in human messages
    // Randomly select 4 incidents from domainQuestions
    currentSize = selectedIndices.size;
    while (selectedIndices.size < currentSize + 4) {
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

    displayIncident();
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

function validateAndStorePersonality(e, formElement) {
    e.preventDefault();

    summativeSubmitBtn = document.getElementById('summativePersonalityBtn');
    summativeSubmitBtn.disabled = true;

    const formData = new FormData(formElement);
    const formValues = {};

    // Check if the all radio questions were answered
    inputKeysValidation = ["pers1"]
    persContext["coworker_inits"] = document.querySelector('input[name="pers1"]').value.trim();
    allKeysExist = inputKeysValidation.every(key => formValues[key]!="");
    allKeysExist = true;
    if (!allKeysExist){
        alert("Please respond to all questions.");

        summativeSubmitBtn.disabled = false;

        return;
    }

    const radios = document.querySelectorAll('input[name="personality"]');
    let selectedValue = null;

    radios.forEach((radio) => {
        if (radio.checked) {
            selectedValue = radio.getAttribute('data-index');
        }
    });

    if (selectedValue) {
        personalityKnown = true;
        persContext["personality"] = defaultPersonalities[selectedValue];
        console.log('Selected personality:', selectedValue);
        document.getElementById('personality-modal').classList.remove('is-active');

        initiateTransition();
    } else {
        alert("Please respond to all questions.");
        summativeSubmitBtn.disabled = false;
    }
}

function validateAndSubmit(e, formElement) {
    e.preventDefault();

    summativeSubmitBtn = document.getElementById('summativeSubmitBtn');
    summativeSubmitBtn.disabled = true;

    const formData = new FormData(formElement);
    const formValues = {};

    // Check if the all radio questions were answered
    inputKeysValidation = ["dat1"]
    formValues["dat1"] = document.querySelector('input[name="dat1"]').value.trim();

    allKeysExist = inputKeysValidation.every(key => formValues[key]!="");
    if (!allKeysExist){
        alert("Please respond to all questions.");

        summativeSubmitBtn.disabled = false;

        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const prolific_id = urlParams.get('PROLIFIC_PID');

    data = formValues
    data['scenario_num'] = currentIncidentIndex
    data['incident_id'] = selectedQuestions[currentIncidentIndex]['ID']

    if (behaviorKnown) {
        data['context_behav'] = document.querySelector('.context-blurb').textContent;
    }
    if (personalityKnown) {
        data['context_pers'] = document.querySelector('.context-blurb').textContent;
    }

    fetch(`/store-summative-writing/${prolific_id}/`, {
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

    var instruction = document.getElementById('instruction');

    if (currentIncidentIndex === indexAtBehavior) {

        instruction.innerHTML = `
        <p>Consider what the representative is going through below. Keep this information in mind as you read the excerpt below.</p>
        <p>&nbsp;</p>
        <p>Read carefully and respond to the prompts. </p>
        `;
    }
    else if (currentIncidentIndex === indexAtPersonality) {
        instruction.innerHTML = `
        <p>Imagine that your coworker, `+persContext['coworker_inits']+` is the representative speaking to the client. Keep their personality in mind as you read the excerpt below. </p>
        <p>&nbsp;</p>
        <p>Read carefully and respond to the prompts.</p>
        `;
    }


    setTimeout(displayIncident, TIMEOUT_DURATION);
}

function initiateTransition() {
    var transitionBlurb = document.getElementById('transition-blurb');

    document.getElementById('survey-modal').classList.remove('is-active');

    if (currentIncidentIndex === indexAtBehavior) {
        transitionBlurb.innerHTML = `
        <p>For the next set of conversation excerpts, you will be given <b>additional information</b> about the representative.</p>
        <p>&nbsp;</p>
        <p>Please read this information carefully and consider it when responding to the questions.</p>
        `;
        behaviorKnown = true;
        personalityKnown = false;
    }
    if (currentIncidentIndex === indexAtPersonality) {
        if (personalityKnown){
            transitionBlurb.innerHTML = `
            <p>For the next set of conversation excerpts, <b>imagine that `+persContext["coworker_inits"]+` is the representative</b> engaging with the client.</p>
            <p>&nbsp;</p>
            <p>Please consider their personality when responding to the questions.</p>`;
        }
        else{
            transitionBlurb.innerHTML = '';
            document.getElementById('personality-modal').classList.add('is-active');
            const form = document.getElementById('summativePhaseIPersonality');
            form.addEventListener('submit', function(e) {
                validateAndStorePersonality(e, this);
            });
            behaviorKnown = false;
        }
    }


    document.getElementById('transition-modal').classList.add('is-active');
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




