
function clickOnEvent(div) {
    if(div.hasClass("active-event")){
    } 
    else {
        $(".active-event").removeClass("active-event").find(".glyphicon-ok").removeClass("glyphicon-ok").addClass("glyphicon-unchecked")
        div.addClass("active-event");
        button = div.find(".glyphicon-unchecked");
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
                var usersEventID = getUsersEventID(data);
                console.log(usersEventID);
                for (var i = 0; i < events.length; i++)
                {
                    if (events[i]['id'] === usersEventID)
                    { 
                        addActiveEventinfo(events[i]); 
                    } else
                    {
                        addEventinfo(events[i]); 
                    }
                    if (events[i]['id'] === group['current_event']['id'])
                    {
                        $('.event-name:eq(' + i + ')').append('\
                            <span class="glyphicon glyphicon-screenshot " aria-hidden="true" style="font-size: 60px; top: 10px;"></span>');
                    }
                }
            } else {
                // Something went wrong in the api call.
                alert("Internal Server Error");
            }
        })}, delay);
});

function getUsersEventID(data)
{
    group = data['group'];
    var userInfo = -1;
    var userID = data['user_id'];
    for (var n = 0; n < group['members'].length; n++)
    {
        if (group['members'][n]['id'] == userID)
        { 
            userInfo = group['members'][n];
        }
    }
    //console.log(userInfo);
    //console.log(userInfo['group_status']['status']['id']);
    //console.log(groups[i]);
    //console.log(groups[i]['current_event']['id']);
    return userInfo['group_status']['status']['id'];

}

function addGroupsCurrentEvent(group)
{
 $(".group-name").after('\
            <div class="event-curr" >\
                    The Group&#8217;s Event\
                    </div>\
                <div class="event-info">\
                    <div class="event-name" style="font-size:60px">'
                        + group["current_event"]["title"] + '\
                    </div>\
                    <div class="event-time">'
                        + parseTime(group["current_event"]["time"]) + '\
                    </div>\
                    <div class="event-location">'
                        + group["current_event"]["location_name"] + '\
                    </div>\
                </div>');
}

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
    $(".group-name").css("opacity", ".3");
    window.location.href = '../home/?id=' + groupid;
}
function setGroupEvent(){
    var eventid = $(".active-event").attr('id');
    var groupid = $(".glyphicon-arrow-left").attr('id');
    $('#group-event').css('opacity', '.3'); 
    
    api_groups_currentevent(groupid, eventid,'false', function(data) {
        if (data['accepted'])
        {
            window.location.href = '../home?id=' + groupid;
        }
    });
}
function setPersonalEvent(){
    var eventid = $(".active-event").attr('id');
    var groupid = $(".glyphicon-arrow-left").attr('id');
    $('#your-event').css('opacity', '.3'); 
    api_groups_currentevent(groupid, eventid,'true', function(data) {
        if (data['accepted'])
        {
            window.location.href = '../home?id=' + groupid;
        }
    });
}
