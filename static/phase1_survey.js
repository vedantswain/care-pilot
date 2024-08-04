const indexAtBehavior = 2;
const indexAtPersonality = 4;

var personalityKnown = false;

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
            setTimeout(initiateTransition, 3000);
        }
        setTimeout(displayIncident, 3000);
    } else {
        document.getElementById('end-modal').classList.add('is-active');
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
    allKeysExist = true;
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
    }
    if (currentIncidentIndex === indexAtPersonality && personalityKnown === false) {
        transitionBlurb.innerHTML = '';
        document.getElementById('personality-modal').classList.add('is-active');
    }


    document.getElementById('transition-modal').classList.add('is-active');
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('transition-modal').classList.add('is-active');

    var nextBtn = document.getElementById('summativeNextBtn');
    nextBtn.addEventListener('click', initiateNextPart);

    const urlParams = new URLSearchParams(window.location.search);
    const domain_from_url = urlParams.get('domain');

    loadIncidents(domain_from_url);

    const form = document.getElementById('summativePhaseI');
    form.addEventListener('submit', function(e) {
        validateAndSubmit(e, this);
    });
});
