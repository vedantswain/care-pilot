const indexAtBehavior = 2;
const indexAtPersonality = 4;

TIMEOUT_DURATION = 1000;

var defaultDomains = ["mobile-device", "hotel", "airlines"];

var personalityKnown = false;
var persContext = {};

var defaultPersonalities = [
    "They are organized and dependable. They tend to remain composed when facing challenges, but are prone to setting unrealistic expectations.",
    "They are outgoing, competitive, and high energy. They tend to work on impulse, but are also prone to frustration.",
    "They are detail-oriented and reliable but might appear distant. They tend to work carefully, but are prone to overthinking."
]

var behaviorKnown = false;

var defaultBehaviors = [
    "The conversation takes place about 2 hours into the work shift. The representative has already addressed a few customer complaints before the following incident.",
    "The conversation takes place in the second half of the work shift. The representative has been working longer hours over the past few days and has not been taking breaks.",
    "The conversation takes place at the middle of the work shift. The representative has been spending minimal time on tasks and has been regularly checking their personal messages."
];

var remainingBehaviors = [];

const selectedQuestions = [];
var currentIncidentIndex = 0;

function getDataFromTSV(data) {
    var lines = data.split("\n");
    var result = [];
    var headers = lines[0].split("\t");

    for (var i = 1; i < lines.length; i++) {
        var obj = {};
        var currentline = lines[i].split("\t");

        for (var j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentline[j];
        }

        result.push(obj);
    }
    return result;
}

function getBehaviorContext() {
    var qContainer = document.getElementById("qContainer");

    if (remainingBehaviors.length === 0){
        remainingBehaviors = defaultBehaviors;
    }

    var behaviorIndex = Math.floor(Math.random() * remainingBehaviors.length);
    var selectedBehavior = remainingBehaviors.splice(behaviorIndex, 1)[0];

    var header = document.createElement('h2');
    header.classList.add("context-blurb");
    header.textContent = "" + selectedBehavior;

    qContainer.prepend(header);

    console.log("Behavior Header and Incident HTML appended to container");
}

function getPersonalityContext() {
    var qContainer = document.getElementById("qContainer");

    var header = document.createElement('h2');
    header.classList.add("context-blurb");
    header.textContent = persContext["personality"];

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
    addMessage(conversation["Follow-up Complaint 2\r"], 'customer');

    return container;
}

function displayIncident() {
    var qContainer = document.getElementById("qContainer");

    var qContainer = document.getElementById("qContainer");
    qContainer.innerHTML = '';
    document.querySelector('input[name="dat1"]').value = "";
    document.querySelector('input[name="dat2"]').value = "";
    document.querySelector('textarea[name="dat3"]').value = "";
    document.querySelector('textarea[name="dat4"]').value = "";

    document.querySelector('input[name="dat1"]').disabled = false;
    document.querySelector('input[name="dat2"]').disabled = false;
    document.querySelector('textarea[name="dat3"]').disabled = false;
    document.querySelector('textarea[name="dat4"]').disabled = false;

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
        var question = incidentData;
        var incidentHTML = createConversationHTML(question);

        if (behaviorKnown && incidentIndex >= indexAtBehavior) {
            getBehaviorContext();
        }
        if (personalityKnown && incidentIndex >= indexAtPersonality) {
            getPersonalityContext();
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
    document.querySelector('input[name="dat2"]').disabled = true;
    document.querySelector('textarea[name="dat3"]').disabled = true;
    document.querySelector('textarea[name="dat4"]').disabled = true;

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


function loadIncidents(domain){
    // Define a list of possible domains
//    var domains = ["mobile-device", "hotel", "airlines"];
//    // Randomly select a domain
//    var randomDomain = domains[Math.floor(Math.random() * domains.length)];

    var randomDomain = domain;
    console.log("Selected Domain: " + randomDomain);

    var url = "/summative/phase1/get-tsv/";
    var qContainer = document.getElementById("qContainer");

    jQuery.ajax({
        url: url,
        dataType: "text",
        success: function(data) {
            var results = getDataFromTSV(data);
            console.log("Parsed Results:", results);

            // Filter questions by selected domain
            var domainQuestions = results.filter(q => q['Domain'] === randomDomain);
            console.log("Domain Questions: ", domainQuestions);

            // Define categories
            var categories = ["Service Quality", "Product Issues", "Pricing and Charges", "Policy", "Resolution"];

            // Select one question from each category and one random question
            var usedIndices = new Set();

            categories.forEach(category => {
                var categoryQuestions = domainQuestions.filter(q => q['Category'] === category);
                if (categoryQuestions.length > 0) {
                    var randomIndex = Math.floor(Math.random() * categoryQuestions.length);
                    selectedQuestions.push(categoryQuestions[randomIndex]);
                    usedIndices.add(categoryQuestions[randomIndex]['ID']);
                }
            });

            // Select the 6th question randomly from the remaining questions
            var remainingQuestions = domainQuestions.filter(q => !usedIndices.has(q['ID']));
            if (remainingQuestions.length > 0) {
                var randomIndex = Math.floor(Math.random() * remainingQuestions.length);
                selectedQuestions.push(remainingQuestions[randomIndex]);
            }

            console.log("Selected Questions: ", selectedQuestions);

            displayIncident();
            // Store selected questions and domain in embedded data fields
//            Qualtrics.SurveyEngine.setEmbeddedData("selectedDomain", randomDomain);
//            selectedQuestions.forEach((question, index) => {
//                Qualtrics.SurveyEngine.setEmbeddedData("incident_" + (index + 1), JSON.stringify(question));
//            });


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
    inputKeysValidation = ["dat1","dat2","dat3","dat4"]
    formValues["dat1"] = document.querySelector('input[name="dat1"]').value.trim();
    formValues["dat2"] = document.querySelector('input[name="dat2"]').value.trim();
    formValues["dat3"] = document.querySelector('textarea[name="dat3"]').value.trim();
    formValues["dat4"] = document.querySelector('textarea[name="dat4"]').value.trim();

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
        data['context'] = document.querySelector('.context-blurb').textContent;
    }
    if (personalityKnown) {
        data['context'] = document.querySelector('.context-blurb').textContent;
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




