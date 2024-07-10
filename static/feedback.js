const sliderValues = {};

function updateSlider(sliderName, slideAmount) {
    // Store the slider value in the dictionary
    sliderValues[sliderName] = slideAmount;
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

function completeSurvey() {
    window.location.href = '/complete';
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feedbackForm');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const submitterButton = e.submitter.id;

        const formData = new FormData(this);
        const formValues = {};
        formData.forEach((value, key) => { formValues[key] = value; });

        // Check if the all radio questions were answered
        radioKeysValidation = ["interaction_polite","interaction_dignity","interaction_respect","cognitive_demands","cognitive_resources"]
        allKeysExist = radioKeysValidation.every(key => Object.keys(formValues).includes(key));
        if (!allKeysExist){
            alert("Please respond to all radio button questions.");
            return;
        }
        // Check if the all slider questions were answered. Need to check different dictionary because of default slider values.
        sliderKeysValidation = ["affect_valence","affect_arousal","support_effective","support_helpful", "support_beneficial", "support_adequate", "support_sensitive", "support_caring", "support_understanding", "support_supportive"]
        allKeysExist = sliderKeysValidation.every(key => Object.keys(sliderValues).includes(key));
        if (!allKeysExist){
            alert("Please respond to all slider questions. If you would like to keep the value at the starting position, please move the slider back and forth to confirm your selection.");
            return;
        }
        const sessionId = window.location.pathname.split('/')[1];
        const clientId = sessionStorage.getItem('client_id');

        data = formValues
        data['client_id'] = clientId

        fetch(`/${sessionId}/store-survey`, {
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
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Feedback submitted successfully!');

            if (submitterButton == "completeButton") {
                completeSurvey();
            }
            else {
                updateClientQueue();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error submitting feedback');
        });
    });
});
