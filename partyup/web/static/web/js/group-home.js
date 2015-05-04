// Carousel actions
function carouselClick(div){
      $( ".active-indicator" ).removeClass("active-indicator");
      console.log(div)
      div.addClass("active-indicator");
}

/**
 * Get all of the users groups, and generate the home page.
 * TODO: refactor so delay is more intuitive
 */
$(document).ready(function() {
    // Get groups and perform callback function
    var delay = 400;
    setTimeout(function() {
        api_groups_get("attending", function(data) {
            $("#loader").remove();
            if (data["accepted"]) {
                var groups = data["groups"];
                var numGroups = groups.length;
                if (numGroups == 0) {
                    // Redirect to some other page in the app. Not sure about what to do.
                } else {
                    // Print out all of the groups
                    for (var i = 0; i < numGroups; i++) {
                        if (i == 0) {
                            // Mark first group as active
                            addActiveGroup(groups[i]);
                            if (numGroups > 1) {
                                addActiveIndicator(i);
                            }
                        } else {
                            addGroup(groups[i]);
                            addIndicator(i);
                        }
                    }
                }
            } else {
                // Something went wrong in the api call.
                alert("butts");
            }
        })}, delay);
});

/**
 * Convert time in the form "2015-04-16 19:49:00+00:00" to 
 * "3:49 pm Thursday April 16" using moment.js
 */
function parseTime(time) {
    return moment(time).format("LLLL");
}

/**
 * Write the html for an active group.
 */
function addActiveGroup(group) {
    $(".carousel-inner").append('\
        <div class="item active">\
            <div class="group-name">'
            + group["title"] + '\
            </div>\
            <div class="event-curr">\
                    Current Event <span class="glyphicon glyphicon-cog" \
                aria-hidden="true" \
                style="top: 10; left: 20;"></span>\
                </div>\
                <div class="event-info">\
                    <div class="event-name">'
                        + group["current_event"]["title"] + '\
                    </div>\
                    <div class="event-time">'
                        + parseTime(group["current_event"]["time"]) + '\
                    </div>\
                    <div class="event-location">'
                        + group["current_event"]["location_name"] + '\
                    </div>\
                </div>\
                <div class="chat-button">\
                    Chat\
                </div>\
                <div class="ping-button">\
                    Ping Group\
                </div>\
                <div class="edit-button">\
                    Edit Group\
                </div>\
            </div>\
        <div>\
    ');        
}

/**
 * Write the html for a group.
 */
function addGroup(group) {
    $(".carousel-inner").append('\
        <div class="item">\
            <div class="group-name">'
            + group["title"] + '\
            </div>\
            <div class="event-curr">\
                    Current Event <span class="glyphicon glyphicon-cog" \
                aria-hidden="true" \
                style="top: 10; left: 20;"></span>\
                </div>\
                <div class="event-info">\
                    <div class="event-name">'
                        + group["current_event"]["title"] + '\
                    </div>\
                    <div class="event-time">'
                        + parseTime(group["current_event"]["time"]) + '\
                    </div>\
                    <div class="event-location">'
                        + group["current_event"]["location_name"] + '\
                    </div>\
                </div>\
                <div class="chat-button">\
                    Chat\
                </div>\
                <div class="ping-button">\
                    Ping Group\
                </div>\
                <div class="edit-button">\
                    Edit Group\
                </div>\
            </div>\
        <div>\
    ');        
}

/**
 * Add an active indicator for the nth group.
 */
function addActiveIndicator(n) {
    $(".carousel-indicators").append(
        '<li data-target="#group-carousel" data-slide-to="' 
        + n + 
        '" class="active-indicator" onclick="carouselClick($(this))"></li>'
    );
}

/**
 * Add an indicator for the nth group.
 */
function addIndicator(n) {
    $(".carousel-indicators").append(
        '<li data-target="#group-carousel" data-slide-to="'
        + n +
        '"onclick="carouselClick($(this))"></li>'
    );
}
