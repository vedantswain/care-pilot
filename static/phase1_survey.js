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

function displayIncident(incidentIndex) {
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

            displayIncident(currentIncidentIndex);
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
        }
        alert('Feedback submitted successfully!');
        window.location.href = response.url
        // return response.json();
    })
    // .then(data => {
    //     console.log('Success:', data);
    //     alert('Feedback submitted successfully!');
    //     // updateClientQueue();
    // })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error submitting response. Please try again.');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('start-modal').classList.add('is-active');

    const urlParams = new URLSearchParams(window.location.search);
    const domain_from_url = urlParams.get('domain');

    loadIncidents(domain_from_url);

    const form = document.getElementById('summativePhaseI');
    form.addEventListener('submit', function(e) {
        validateAndSubmit(e, this);
    });
});
