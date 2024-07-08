const sliderValues = {};

function updateSlider(sliderName, slideAmount) {
    // Store the slider value in the dictionary
    sliderValues[sliderName] = slideAmount;
}

// function updateClientQueue() {
//     const sessionId = window.location.pathname.split('/')[1];

//     fetch(`/${sessionId}/update-clientQueue`)
//     .then(response => response.json())
//     .then(data => {
//         if (data.url) {
//             window.location.href = data.url;
//         }
//     })
//     .catch(error => console.error('Error updating client queue:', error));
// }

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('start-modal').classList.add('is-active');

    const form = document.getElementById('preFeedbackForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault(); 
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
        sliderKeysValidation = ["affect_valence","affect_arousal" ]
        allKeysExist = sliderKeysValidation.every(key => Object.keys(sliderValues).includes(key));
        if (!allKeysExist){
            alert("Please respond to all slider questions. If you would like to keep the value at the starting position, please move the slider back and forth to confirm your selection.");
            return;
        }
        const sessionId = window.location.pathname.split('/')[1];
        const clientParam = window.location.href.split('?')[1];

        data = formValues
        data['client_param'] = clientParam

        fetch(`/${sessionId}/store-pre-task-survey`, {
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
            alert('Error submitting feedback');
        });
    });
});
