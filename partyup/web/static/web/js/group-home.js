
function carouselClick(div){
	$( ".active-indicator" ).removeClass("active-indicator");
	console.log(div)
	div.addClass("active-indicator");	

}

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
