document.getElementById('search-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent form from submitting the default way
    const query = document.getElementById('query').value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${query}`,
    })
    .then(response => response.json())
    .then(data => {
        const photosDiv = document.getElementById('photos');
        photosDiv.innerHTML = ''; // Clear previous results

        if (data.photos && data.photos.length > 0) {
            const photo = data.photos[0];
            const imgElement = document.createElement('img');
            imgElement.src = photo.src.large2x;
            imgElement.alt = photo.alt;

            const photographer = document.createElement('p');
            photographer.innerHTML = `Photo by <a href="${photo.photographer_url}" target="_blank">${photo.photographer}</a>`;

            photosDiv.appendChild(imgElement);
            photosDiv.appendChild(photographer);
        } else {
            photosDiv.innerHTML = 'No photos found.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
