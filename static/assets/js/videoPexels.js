// window.onload = function() {
//     const searchForm = document.getElementById('search-form');

//     // Handle form submission for search
//     searchForm.addEventListener('submit', function(event) {
//         event.preventDefault();

//         const query = document.getElementById('search-query').value;
//         fetchVideo(query);
//     });

//     // Fetch video function
//     function fetchVideo(query) {
//         fetch(`/get_video?query=${encodeURIComponent(query)}`)
//         .then(response => response.json())
//         .then(data => {
//             if (data.error) {
//                 console.error('Error fetching video:', data.error);
//                 return;
//             }

//             // Set video source
//             const videoSource = document.getElementById('video-source');
//             videoSource.src = data.video_url;
            
//             // Set author link
//             const authorLink = document.getElementById('author-link');
//             authorLink.textContent = data.author_name;
//             authorLink.href = data.author_url;
            
//             // Load video
//             const videoPlayer = document.getElementById('video-player');
//             videoPlayer.load();
//         })
//         .catch(error => console.error('Error fetching video data:', error));
//     }

//     // Fetch a default video on page load (optional)
//     fetchVideo('nature');
// };


window.onload = function() {
    const form = document.getElementById('video-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const videoId = document.getElementById('video-id').value;

        // Fetch video data from the backend with the provided video ID
        fetch('/get_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ video_id: videoId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching video:', data.error);
                return;
            }

            // Set the video source
            const videoSource = document.getElementById('video-source');
            videoSource.src = data.video_url;
            
            // Set author link
            const authorLink = document.getElementById('author-link');
            authorLink.textContent = data.author_name;
            authorLink.href = data.author_url;
            
            // Load the video and display the video player and author info
            const videoPlayer = document.getElementById('video-player');
            const authorInfo = document.getElementById('author-info');
            videoPlayer.style.display = 'block';
            authorInfo.style.display = 'block';
            videoPlayer.load();

            // Display thumbnails
            const thumbnailsContainer = document.getElementById('thumbnails');
            thumbnailsContainer.innerHTML = ''; // Clear any previous thumbnails
            data.thumbnails.forEach((thumbnail, index) => {
                const img = document.createElement('img');
                img.src = thumbnail;
                img.alt = `Thumbnail ${index}`;
                img.style.width = '100px';
                img.style.height = 'auto';
                thumbnailsContainer.appendChild(img);
            });
            thumbnailsContainer.style.display = 'block';
        })
        .catch(error => console.error('Error fetching video data:', error));
    });
};



