function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
}    

function clickOnEvent(div) {
    if(div.hasClass("active-event")){
        div.removeClass("active-event");
        button = div.find(".glyphicon");
        button.removeClass("glyphicon-ok").addClass("glyphicon-unchecked");
    } 
    else {
        $(".active-event").removeClass("active-event").find(".glyphicon").removeClass("glyphicon-ok").addClass("glyphicon-unchecked")
        div.addClass("active-event");
        button = div.find(".glyphicon");
        button.removeClass("glyphicon-unchecked").addClass("glyphicon-ok");
        
    } 
}

$(document).ready(function() {
    var delay = 400;
    setTimeout(function() {
        api_groups_getid(getUrlParameter('id'), function(data) {
            $("#loader").css('display', "None");
            $('.shade').fadeOut();
            if (data["accepted"]) {
                var group = data["group"];
                var events = group["events"];
                $('.group-name').append('\
                        <span class="glyphicon glyphicon-arrow-left   " aria-hidden="true" style="font-size: 70px;\
                        top: -5px;\
                        padding-right: 10px;\
                        left: -20px;"></span>'
                        + group['title']);
                for (var i = 0; i < events.length; i++)
                {
                   addEventinfo(events[i]); 
                }
            } else {
                // Something went wrong in the api call.
                alert("butts");
            }
        })}, delay);
});

function addEventinfo(eventObj) {
    $(".group-events").append('\
        <div class="event-info" style="border-top:none" onclick="clickOnEvent($(this))">\
            <div class="event-choose-button">\
                <span class="glyphicon  glyphicon-unchecked " aria-hidden="true" style="font-size: 130px;\
                left: -20px;\
                top: 10px; \
                "></span>\
            </div>\
            <div class="inner-event-info">\
                <div class="event-name" style="font-size:60px;">'
                    + eventObj['title'] + '\
                </div>\
                <div class="event-time" style="font-size:15px;">'
                    + parseTime(eventObj['time']) + '\
                </div>\
                <div class="event-location" style="font-size:60px;">'
                    + eventObj['location_name'] + '\
                </div>\
            </div>\
        </div>\
            ');
}
/**
 * Convert time in the form "2015-04-16 19:49:00+00:00" to 
 * "3:49 pm Thursday April 16" using moment.js
 */
function parseTime(time) {
    return moment(time).format("LLLL");
}
