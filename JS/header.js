$( document ).load(function() {
  	

	var currentURL = window.location.href; 
	var e = jQuery.Event("click");
	e.ctrlKey = true;
	$('a').trigger(e);


});
