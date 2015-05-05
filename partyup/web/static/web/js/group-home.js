
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
            $("#loader").css('display', "None");
            $('.shade').fadeOut();
            if (data["accepted"]) {
                var groups = data["groups"];
                var numGroups = groups.length;
                if (numGroups == 0) {
                    // Redirect to some other page in the app. Not sure about what to do.
                    noGroupsPage();
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
                    addSwipeFunction();
                }
            } else {
                // Something went wrong in the api call.
                alert("butts");
            }
        })}, delay);
});

/**
 * Print out a blank page if the user doesn't have any groups.
 */
function noGroupsPage() {
    $(".carousel-inner").append('\
        <div style="padding-top:100px;font-size:xx-large;">You don\'t have any groups.</div>\
    ');
}

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
                <div class="event-warning">\
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
                <div class="chat-button"id="'+ group["id"] + '"  >\
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
function addGroupWarning(numGroup){
    itemDiv = $(".event-warning:eq(" + numGroup +")")
    itemDiv.css("display","block");
    itemDiv.append('\
                <div class="event-warning-icon">\
                     <span class="glyphicon glyphicon-bullhorn" \
                aria-hidden="true" \
                style="  top: 25px; left: 10px;"></span>\
                </div>\
                <div class="event-warning-text"> You are currently not with your group! Tap to update.</div>\
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
                <div class="event-warning">\
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
                <div class="chat-button" id="'+ group["id"] + '" >\
                    Chat\
                </div>\
                <div class="ping-button" id="'+ group["id"] + '" >\
                    Group&#8217;s Status\
                </div>\
                <div class="edit-button" id="'+ group["id"] + '" >\
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
                /*$(document).ready(function() {  */
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
                /*});*/
        '</script>'
    );
}

// function for the ping page. It belongs here though, show it some love
function pingMemberClick(div){
	if(div.hasClass("ping-member-name")){
	// slide all of the other active ones uo 
	$( ".ping-member-name-active").each(function( i ) {
		$(this).addClass("ping-member-name").removeClass("ping-member-name-active");
		$(this).find("span").removeClass("glyphicon-menu-down").addClass("glyphicon-menu-right")
		$(this).next().slideUp()
	})
	// slide this one down
	div.addClass("ping-member-name-active").removeClass("ping-member-name");
	div.find("span").removeClass("glyphicon-menu-right").addClass("glyphicon-menu-down")
	div.next().slideDown()
	}

	else if(div.hasClass("ping-member-name-active")){
	div.addClass("ping-member-name").removeClass("ping-member-name-active");
	div.find("span").removeClass("glyphicon-menu-down").addClass("glyphicon-menu-right")
	div.next().slideUp()
	}
}

// function called when the ping button is pressed
function pingbuttonclick(div)
{

}

// function called when the group status button is pressed
function statusButtonClick(div)
{
    groupid = div.attr('id');
    window.location.href = '../ping/?id=' + groupid;
}

// function called when the group events button is pressed
function eventsButtonClick(div)
{
    groupid = div.attr('id');
    window.location.href = '../events/?id=' + groupid;
}
