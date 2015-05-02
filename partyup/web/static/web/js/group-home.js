// Carousel actions
function carouselClick(div){
      $( ".active-indicator" ).removeClass("active-indicator");
      console.log(div)
      div.addClass("active-indicator");
}