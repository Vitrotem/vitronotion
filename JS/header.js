$( document ).load(function() {
  	

	var currentURL = (window.location != window.parent.location)
            ? document.referrer
            : document.location.href;
	
	var e = jQuery.Event("click");
	e.ctrlKey = true;
	$('a').trigger(e);


});
