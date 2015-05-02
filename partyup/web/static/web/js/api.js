// Library for API calls
var server = "";

// Initialize the API
function set_server(s) {
    server = s + "/api";
    console.log(server);
}


// Get groups for the current user. Returns a JSON.
// Function assumes that the user is logged in
function groups_get() {
    console.log("hello world");
}

// Logs in the user asynchronously. Calls the given callback function when
// the request is complete
function accounts_login(username, password, deviceID, callback) {
    var url = server + "/users/login/";
    var data = {
        username: username,
        password: password,
        deviceID: deviceID,
    };

    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        contentType: 'text/plain',
        xhrFields: {
            withCredentials: true
        },
        success: callback,
    });
}