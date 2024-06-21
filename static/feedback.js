document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feedbackForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault(); 
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => { data[key] = value; });

        const sessionId = window.location.pathname.split('/')[1];

        fetch(`/${sessionId}/get-survey`, {
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
            document.getElementById('surveyModal').style.display = 'none';  

            fetch(`/chat`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                window.location.href = '/chat'; 
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error starting new chat');
            });
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error submitting feedback');
        });
    });
});

// document.addEventListener('DOMContentLoaded', function () {
//     const form = document.getElementById('feedbackForm');
//     form.addEventListener('submit', function (e) {
//         e.preventDefault();
//         const formData = new FormData(this);
//         const data = {};
//         formData.forEach((value, key) => { data[key] = value; });

//         const sessionId = window.location.pathname.split('/')[1];

//         fetch(`/${sessionId}/get-survey`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify(data)
//         })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => {
//             console.log('Success:', data);
//             alert('Feedback submitted successfully!');
//             document.getElementById('surveyModal').style.display = 'none';

//             fetch(`/${sessionId}/get-reply`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ start_new_chat: true })
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error('Network response was not ok');
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 window.location.href = data.new_chat_url;
//             })
//             .catch((error) => {
//                 console.error('Error:', error);
//                 alert('Error starting new chat');
//             });
//         })
//         .catch((error) => {
//             console.error('Error:', error);
//             alert('Error submitting feedback');
//         });
//     });
// });
