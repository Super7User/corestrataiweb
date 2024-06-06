function searchItems() {
    // Get the value of the search input
    var searchQuery = document.getElementById('search-box').value.toLowerCase();

    // Get the currently active category, if there is one
    var activeCategory = document.querySelector('.category-button.active');
    var categoryFilter = activeCategory ? activeCategory.getAttribute('data-category') : null;

    // Combine both search and category in the fetch query
    var queryString = `?search=${encodeURIComponent(searchQuery)}`;
    if (categoryFilter) {
        queryString += `&category=${encodeURIComponent(categoryFilter)}`;
    }

    // Send a request to the server with the search query and selected category
    fetch(queryString)
        .then(response => response.text())
        .then(html => {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            var newContent = doc.querySelector('.card-container');
            document.querySelector('.card-container').innerHTML = newContent.innerHTML;
        })
        .catch(error => console.error('Error fetching filtered content:', error));
}



function filterCategory(button) {
    var category = button.getAttribute('data-category');

    fetch(`/?category=${encodeURIComponent(category)}`)
        .then(response => response.text())
        .then(html => {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            var newContent = doc.querySelector('.card-container');
            if (newContent) {
                document.querySelector('.card-container').innerHTML = newContent.innerHTML;
                setActiveCategory(button);
            } else {
                console.error('No .card-container found in the response HTML.');
            }
        })
        .catch(error => console.error('Error fetching filtered content:', error));
}

function setActiveCategory(activeButton) {
    document.querySelectorAll('.category-button').forEach(button => {
        button.classList.remove('active');
    });
    activeButton.classList.add('active');
}




