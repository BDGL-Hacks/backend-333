
function clickOnEvent(div) {
    if(div.hasClass("active-event")){
    } 
    else {
        $(".active-event").removeClass("active-event").find(".glyphicon").removeClass("glyphicon-ok").addClass("glyphicon-unchecked")
        div.addClass("active-event");
        button = div.find(".glyphicon");
        button.removeClass("glyphicon-unchecked").addClass("glyphicon-ok");
        
    } 
}

$(document).ready(function() {
    var delay = 0;
    var groupid = getUrlParameter('id');
    setTimeout(function() {
        api_groups_getid(groupid, function(data) {
            $("#loader").css('display', "None");
            $('.group-name').attr('onclick', 'groupBackClick(' + groupid +')');
            if (data["accepted"]) {
                var group = data["group"];
                var events = group["events"];
                var adminID = group['is_admin'];
                if (!adminID) { $("#group-event").css("display","none");}; 
                console.log(adminID);
                $('.group-name').append('\
                        <span class="glyphicon glyphicon-arrow-left   " aria-hidden="true" id="' + groupid + '"style="font-size: 70px;\
                        top: -5px;\
                        padding-right: 10px;\
                        left: -20px;"></span>'
                        + group['title']);
                for (var i = 0; i < events.length; i++)
                {
                    if (events[i]['id'] === group['current_event']['id'])
                    { 
                        addActiveEventinfo(events[i]); 
                    } else
                    {
                        addEventinfo(events[i]); 
                    }
                }
            } else {
                // Something went wrong in the api call.
                alert("butts");
            }
        })}, delay);
});

function addActiveEventinfo(eventObj) {
    $(".group-events").append('\
        <div class="event-info active-event" style="border-top:none" onclick="clickOnEvent($(this))" id="' + eventObj['id'] + '">\
            <div class="event-choose-button">\
                <span class="glyphicon  glyphicon-ok " aria-hidden="true" style="font-size: 130px;\
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

function addEventinfo(eventObj) {
    $(".group-events").append('\
        <div class="event-info" style="border-top:none" onclick="clickOnEvent($(this))" id="' + eventObj['id'] + '">\
            <div class="event-choose-button">\
                <span class="glyphicon  glyphicon-unchecked " aria-hidden="true" style="font-size: 130px;\
                left: -20px;\
                top: 10px; \
                "></span>\
            </div>\
            <div class="inner-event-info" >\
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

function groupBackClick(groupid) {
    window.location.href = '../home/?id=' + groupid;
}
function setGroupEvent(){
    var eventid = $(".active-event").attr('id');
    var groupid = $(".glyphicon-arrow-left").attr('id');
    
    api_groups_currentevent(groupid, eventid, function(data) {
        if (data['accepted'])
        {
            window.location.href = '../home?id=' + groupid;
        }
    });
}
function setPersonalEvent(){
    console.log("Personal Event!");
}
