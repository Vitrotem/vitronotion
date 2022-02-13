$( document ).load(function() {
  	


	var e = jQuery.Event("click");
	e.ctrlKey = true;
	$('a').trigger(e);


});
