document.getElementById('input-text').addEventListener('input', validateFields);
document.getElementById('textarea-input').addEventListener('input', validateFields);

function validateFields() {
    const inputText = document.getElementById('input-text').value.trim();
    const textareaInput = document.getElementById('textarea-input').value.trim();
    const generateButton = document.getElementById('generate-button');

    generateButton.disabled = !(inputText && textareaInput);
}

function generate() {
    const input = document.getElementById('input-text').value;
    const textareaInput = document.getElementById('textarea-input').value;

    if (!input || !textareaInput) {
        validateFields();
        return;
    }

    // Show the loading indicator
    document.getElementById('loading-indicator').style.display = 'block';

    fetch('/generate-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: input, textareaInput: textareaInput })
    })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');

            let output = document.getElementById('output-text');
            output.value = '';  // Clear previous contents

            // Read the stream
            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        console.log('Stream finished.');

                        // Hide the loading indicator
                        document.getElementById('loading-indicator').style.display = 'none';
                        return;
                    }
                    output.value += decoder.decode(value, { stream: true });
                    read();  // Read the next chunk
                });
            }

            read();  // Start reading the stream
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('output-text').value = 'Error generating content.';

            // Hide the loading indicator
            document.getElementById('loading-indicator').style.display = 'none';
        });
}

function generate_old(event) {
    //event.preventDefault();  // Prevents the default form submission action if called within a form

    // Get the value from the input field
    var input = document.getElementById('input-text').value;

    // Make a fetch request to your Flask endpoint
    fetch('/generate-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: input })
    })
        .then(response => response.json())
        .then(data => {
            // Update the output textarea with the response from the server
            document.getElementById('output-text').value = data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('output-text').value = 'Error generating content.';
        });
}
