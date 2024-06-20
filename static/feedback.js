


document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feedbackForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault(); 
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => { data[key] = value; });

        const url = '/get-survey';

        fetch(url, {
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
            window.location.href = '/chat'; 
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error submitting feedback');
        });
    });
});

// document.addEventListener('DOMContentLoaded', function() {
//     const form = document.getElementById('feedbackForm');
//     form.addEventListener('submit', function(e) {
//         e.preventDefault(); 
//         const formData = new FormData(this);
//         const data = {};
//         formData.forEach((value, key) => { data[key] = value; });

//         const sessionId = window.location.pathname.split('/')[1]; // Assuming session ID is in the URL

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
//             document.getElementById('surveyModal').style.display = 'none';  // 关闭模态框
//             window.location.href = '/chat'; // 重定向到聊天页面
//         })
//         .catch((error) => {
//             console.error('Error:', error);
//             alert('Error submitting feedback');
//         });
//     });
// });
