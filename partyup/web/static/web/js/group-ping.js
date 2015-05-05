/**
 * Open and close drop down menus that display user status.
 */
function pingMemberClick(div){
    if (div.hasClass("ping-member-name")) {
        // slide all of the other active ones up
        $( ".ping-member-name-active").each(function( i ) {
            $(this).addClass("ping-member-name").removeClass("ping-member-name-active");
            $(this).find("span").removeClass("glyphicon-menu-down").addClass("glyphicon-menu-right")
            $(this).next().slideUp()
        });
        // slide this one down
        div.addClass("ping-member-name-active").removeClass("ping-member-name");
        div.find("span").removeClass("glyphicon-menu-right").addClass("glyphicon-menu-down")
        div.next().slideDown()
    } else if (div.hasClass("ping-member-name-active")) {
        div.addClass("ping-member-name").removeClass("ping-member-name-active");
        div.find("span").removeClass("glyphicon-menu-down").addClass("glyphicon-menu-right")
        div.next().slideUp()
    }
}


/**
 * Generate the proper HTML for the given group.
 */
$(document).ready(function() {
    api_groups_getid(1, function(data) {
        if (data["accepted"]) {
            // Add title
            addTitle(data["group"]["title"]);

            // Print out the group members
            var group_members = data["group"]["members"];

            for (var i = 0; i < group_members.length; i++) {
                addGroupMember(group_members[i]);
            }
        } else {
            // things are very wrong.
            alert("butts");
        }
    });
});


/** 
 * Add the HTML for the group's title.
 */
function addTitle(title) {
    $(".group-name-fixed").append('\
        <span class="glyphicon glyphicon-arrow-left   "\
            aria-hidden="true"\
            style="font-size: 70px;\
            top: -5px;\
            padding-right: 10px;\
            left: -20px;"></span>' 
        + title
    );      
}


/**
 * Add the HTML for the given group member
 */
function addGroupMember(member) {
    // Set appropriate indicator
    var indicator = member["group_status"]["indicator"];
    var indicator_class;
    if (indicator == 0) {
        indicator_class = "ping-members-status";
    } else if (indicator == 1) {
        indicator_class = "ping-members-status status-neutral";
    } else if (indicator == 2) {
        indicator_class = "ping-members-status status-bad";
    }

    // Generate the html
    $(".ping-members").append('\
        <div class="ping-member ">\
            <div class="ping-member-name" onclick="pingMemberClick($(this))">\
                <span class="glyphicon glyphicon-menu-right  " aria-hidden="true"></span>'
                + member['first_name'] + ' ' + member['last_name'] +
                '<div class="' + indicator_class + '"></div>\
            </div>\
            <div class="ping-info">\
                <div class="ping-current-event">\
                    Current Location\
                </div>\
                <div class="ping-current-event-location">'
                    + member["group_status"]["status"]["location_name"] +
                '</div>\
                <div class="ping-send">\
                    Send Ping\
                </div>\
            </div>\
        </div>\
    ');
}