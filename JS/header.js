$( document ).ready(function() {
  	
	$( "iframe" ).setAttribute("id", "test");

	var e = jQuery.Event("click");
	e.ctrlKey = true;
	$('a').trigger(e);


});
