$( document ).ready(function() {
  	
	$( "iframe" ).setAttribute("id", "test");

});

$('a').trigger($.Event("click", { ctrlKey: true }));