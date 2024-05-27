function toggleTheme() {
    document.body.classList.toggle('dark-mode');
}


function toolslogin() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // Simple validation check
    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }
    console.log("It is in javascript")
    // Configure your request
    document.getElementById('user-form').submit();

}
