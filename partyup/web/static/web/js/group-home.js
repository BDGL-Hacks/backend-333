
function carouselClick(div){
      $( ".active-indicator" ).removeClass("active-indicator");
      //console.log(div)
      div.addClass("active-indicator");
}

/**
 * Get all of the users groups, and generate the home page.
 */
$(document).ready(function() {
    // Get groups and perform callback function
    api_groups_get("attending", function(data) {
        $("#loader").css('display', "None");
        var activeID = getUrlParameter('id');
        // if activeID does not exist, then set it to -1
        if (!activeID) {activeID = -1;};
        if (data["accepted"]) {
            var groups = data["groups"];
            var numGroups = groups.length;
            var userID = data['user_id'];
            if (numGroups == 0) {
                // Redirect to some other page in the app. Not sure about what to do.
                console.log("No Groups!")
                noGroupsPage();
            } else {
                // Print out all of the groups
                for (var i = 0; i < numGroups; i++) {
                    // if activeID is true, set groupID active
                    // else have the first group active
                    if ((groups[i]['id'] == activeID) || (activeID == -1 && i == 0)) {
                        // Mark first group as active
                        addActiveGroup(groups[i]);
                        if (numGroups > 1) {
                            addActiveIndicator(i);
                        }
                    } else {
                        addGroup(groups[i]);
                        addIndicator(i);
                    }
                    var userInfo = 0;
                    for (var n = 0; n < groups[i]['members'].length; n++)
                    {
                        if (groups[i]['members'][n]['id'] == userID)
                        { 
                            userInfo = groups[i]['members'][n];
                        }
                    }
                    if (userInfo['group_status']['status']['id'] != groups[i]['current_event']['id'])
                    {
                        addGroupWarning(i, groups[i]['id']);
                    }
                }
                addSwipeFunction();
            }
        } else {
            console.log(data);
            // Something went wrong in the api call.
            alert("Server error while loading doc");
        }
    });
});

/**
 * Print out a blank page if the user doesn't have any groups.
 */
function noGroupsPage() {
    $(".carousel-inner").append('\
        <div style="padding-top:100px;font-size:100px;">You don\'t have any groups.</div>\
    ');
}

/**
 * Write the html for an active group.
 */
function addActiveGroup(group) {
    $(".carousel-inner").append('\
        <div class="item active">\
            <div class="group-name" id="'+ group["id"] + '" onclick="groupEditButtonClick($(this));">'
            + group["title"] + '\
            <span class="glyphicon glyphicon-pencil" aria-hidden="true" style="font-size: 50px; margin-left: 40px;"></span>\
            </div>\
            <div class="event-curr">\
                    Current Event\
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
                <div class="chat-button" id="'+ group["id"] + '" + onclick="chatButtonClick($(this));" >\
                    Chat\
                </div>\
                <div class="ping-button" id="'+ group["id"] + '" onclick="statusButtonClick($(this))">\
                    Group&#8217;s Status\
                </div>\
                <div class="edit-button" id="'+ group["id"] + '" onclick="eventsButtonClick($(this))">\
                    Group&#8217;s Events\
                </div>\
            </div>\
        <div>\
    ');        
}

/**
 * Add a warning if the user is not
 * with his group
 */
function addGroupWarning(numGroup, groupID){
    console.log(numGroup);
    itemDiv = $(".group-name:eq(" + numGroup +")")
    itemDiv.after('\
            <div class="event-warning" onclick="eventsButtonClick($(this))" id="' + groupID +'">\
        <div class="event-warning-icon">\
             <span class="glyphicon glyphicon-bullhorn" \
        aria-hidden="true" \
        style="  top: 25px; left: 10px;"></span>\
        </div>\
        <div class="event-warning-text"> You are currently not with your group! Tap to update.</div>\
                </div>\
    ');
}

/**
 * Write the html for a group.
 */
function addGroup(group) {
    $(".carousel-inner").append('\
        <div class="item">\
            <div class="group-name" id="'+ group["id"] + '" onclick="groupEditButtonClick($(this));">'
            + group["title"] + '\
            <span class="glyphicon glyphicon-pencil" aria-hidden="true" style="font-size: 50px; margin-left: 40px;"></span>\
            </div>\
            <div class="event-curr">\
                    Current Event\
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
                <div class="chat-button" id="'+ group["id"] + '" onclick="chatButtonClick($(this));" >\
                    Chat\
                </div>\
                <div class="ping-button" id="'+ group["id"] + '" onclick="eventsButtonClick($(this))" >\
                    Group&#8217;s Status\
                </div>\
                <div class="edit-button" id="'+ group["id"] + '" onclick="eventsButtonClick($(this))" >\
                    Group&#8217;s Events\
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

/**
 * Add ability to swipe between groups.
 */
function addSwipeFunction() {
    $(".carousel-indicators").after(
            '<script>\n' +
                '$("#group-carousel").swiperight(function() {\n' +
                    '$(this).carousel("prev");\n' +
                    'var indic = $( ".active-indicator");\n' +
                    'var prev = indic.prev();\n' +
                    'if (prev.is("li")){\n' +
                        'indic.removeClass("active-indicator");\n' +
                        'prev.addClass("active-indicator");\n' +
                    '}\n' +
                '});\n' +
                '$("#group-carousel").swipeleft(function() {\n' +
                    '$(this).carousel("next")\n' +
                    'var indic = $( ".active-indicator");\n' +
                    'var next = indic.next();\n' +
                    'if (next.is("li")){\n' +
                        'indic.removeClass("active-indicator");\n' +
                        'next.addClass("active-indicator");\n' +
                    '}\n' +
                '});\n' +
        '</script>'
    );
}

function groupEditButtonClick(div)
{
    groupid = div.attr('id');
    window.location.href = "http://groups-edit?" + groupid;
}
function chatButtonClick(div)
{
    groupid = div.attr('id');
    window.location.href = "http://groups-chat?" + groupid;
}
// function called when the group status button is pressed
function statusButtonClick(div)
{
    groupid = div.attr('id');
    div.css('opacity', '.3');
    window.location.href = '../ping/?id=' + groupid;
}

// function called when the group events button is pressed
function eventsButtonClick(div)
{
    groupid = div.attr('id');
    div.css('opacity', '.3');
    window.location.href = '../events/?id=' + groupid;
}
