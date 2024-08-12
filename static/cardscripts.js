function searchItems() {
    var searchQuery = document.getElementById('search-box').value.toLowerCase();
    var activeCategory = document.querySelector('.category-button.active');
    var categoryFilter = activeCategory ? activeCategory.getAttribute('data-category') : null;

    var queryString = `?search=${encodeURIComponent(searchQuery)}`;
    if (categoryFilter) {
        queryString += `&category=${encodeURIComponent(categoryFilter)}`;
    }

    fetch(queryString)
        .then(response => response.text())
        .then(html => {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            var newContent = doc.querySelector('.card-container');
            if (newContent) {
                document.querySelector('.card-container').innerHTML = newContent.innerHTML;
            } else {
                console.error('No .card-container found in the response HTML.');
            }
        })
        .catch(error => console.error('Error fetching filtered content:', error));
}

function filterCategory(button) {
    const category = button.getAttribute('data-category');
    const buttons = document.querySelectorAll('.category-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    fetch(`/tools?category=${encodeURIComponent(category)}`)
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

document.querySelectorAll('.category-button').forEach(button => {
    button.addEventListener('click', function () {
        filterCategory(button);
    });
});
