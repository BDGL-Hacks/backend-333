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
