// function togglePromptInputs() {
//     var isChecked = document.getElementById('defaultPromptCheckbox').checked;
//     document.getElementById('promptInputs').style.display = isChecked ? 'none' : 'block';
//     document.getElementById('dropdownInputs').style.display = isChecked ? 'block' : 'none';
// }

function updateInputFields() {
    
    var selectedValue = document.getElementById('defaultPromptDropdown').value;
    var negativePrompts = JSON.parse(document.getElementById('negativePromptsData').textContent);

    document.getElementById('promptInput').value = selectedValue;
    if (negativePrompts.hasOwnProperty(selectedValue)) {
        document.getElementById('negativePromptInput').value = negativePrompts[selectedValue];
    } else {
        document.getElementById('negativePromptInput').value = '';
    }
 
}
function generateDescription() {
    let prompt, negativePrompt;
    prompt = document.getElementById('promptInput').value;
    console.log(prompt,"asasas")
    negativePrompt = document.getElementById('negativePromptInput').value;
 
    
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
        }
    })
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);  // Create a URL from the blob
        const imageContainer = document.getElementById('outputImage');
        const outputLink = document.getElementById('outputLink');  
        imageContainer.src = imageUrl;  // Update the image src to the blob URL
        outputLink.href = imageUrl;
        console.log(imageUrl,imageContainer)
    })
    .catch(error => {
        console.error('Error fetching the image:', error);
        alert('Error fetching the image.');
    });
}  

    
function addText() {
    const blogCanvas = document.getElementById('blogCanvas');
    const existingText = blogCanvas.querySelector('p');
    if (existingText) {
        blogCanvas.removeChild(existingText);
    }
    const newText = document.createElement('p');
    newText.textContent = 'Our AI Consulting service is designed to empower businesses by offering expert guidance in General AI, Computer Vision, and Machine Learning. By leveraging our deep industry knowledge and technical expertise, we help organizations navigate the complex landscape of AI implementation. From strategy development to operational execution, we provide tailored solutions that align with your business objectives, ensuring that you stay ahead in the competitive market.';
    blogCanvas.appendChild(newText);
    blogCanvas.focus(); 
}
function addImage() {
    const blogCanvas = document.getElementById('blogCanvas');
    const existingText = blogCanvas.querySelector('img');
    if (existingText) {
        blogCanvas.removeChild(existingText);
    }
    const newImg = document.createElement('img');
    newImg.src = 'static/images/image.png';
    blogCanvas.appendChild(newImg);
    blogCanvas.focus(); 
}
