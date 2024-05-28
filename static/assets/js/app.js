function generateDescription() {
    const prompt = document.getElementById('promptInput').value;
    console.log(prompt,"asasas")
    const negativePrompt = document.getElementById('negativePromptInput').value;

   
    // Example POST request to Flask backend
    fetch('/generate-description', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt, negativePrompt: negativePrompt })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();  // Convert the response to a Blob if the request was successful
        } else {
            throw new Error('Network response was not ok.');
            console.log('Network response was not ok.')
        }
    })
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);  // Create a URL from the blob
        const imageContainer = document.getElementById('outputImage');
        imageContainer.src = imageUrl;  // Update the image src to the blob URL
        console.log(imageUrl,imageContainer)
    })
    .catch(error => {
        console.error('Error fetching the image:', error);
        alert('Error fetching the image.');
    });
}