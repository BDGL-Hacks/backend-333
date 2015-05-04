// Library for API calls

// Get groups of given type for the current user. type may be set to "attending",
// "created", or "invited". Call the given callback function on success, which 
// allows the client to manipulate the JSON returned by the server.
// Function assumes that the user is logged in.
function api_groups_get(type, callback) {
    var url = "/api/groups/get/";
    var data = {type: type};
    $.post(url, data, function(data) {
        if (data.hasOwnProperty("accepted")) {
            if (data["accepted"]) {
                // The JSON returned as kind of an awkward form, so I'm going to
                // parse out the weirdness so only the relevant type is passed to the
                // callback function.
                new_data = {
                    accepted: data["accepted"],
                    groups: data[type]
                };
                callback(new_data);
            } else {
                // Error so no need to parse results
                callback(data);
            }
        }
    });
}

// Logs in the user asynchronously. Calls the given callback function when
// the request is complete
function api_accounts_login(username, password, deviceID, callback) {
    var url = "/api/users/login/";
    var data = {
        username: username,
        password: password,
        deviceID: deviceID,
    };
    $.post(url, data, callback);
}