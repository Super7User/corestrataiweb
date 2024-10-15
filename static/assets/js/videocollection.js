document.addEventListener('DOMContentLoaded', function() {
    const mediaContainer = document.getElementById('mediaContainer');

    // Fetch media data from Flask backend
    fetch('/api/media')
        .then(response => response.json())
        .then(data => {
            const media = data.media;
            media.forEach(item => {
                const mediaItem = document.createElement('div');
                mediaItem.className = 'media-item';

                if (item.type === 'Photo') {
                    // Display image
                    const img = document.createElement('img');
                    img.src = item.src.large;
                    mediaItem.appendChild(img);
                } else if (item.type === 'Video') {
                    // Display video
                    const video = document.createElement('video');
                    video.src = item.video_files[0].link;
                    video.controls = true;
                    mediaItem.appendChild(video);
                }

                mediaContainer.appendChild(mediaItem);
            });
        })
        .catch(error => {
            console.error('Error fetching media:', error);
        });
});
