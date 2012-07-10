$(function(){
	$('.remove').click(removeFeed);

	$('.add').click(addAnother);
});

function removeFeed()
{
	if($("#feed_urls input").length > 1)
	{
		$(this).closest('.control-group').remove()
	}
}

function addAnother()
{
	var group = $(this).closest('.control-group').clone();
	group.find('input').val('');
	group.find('.remove').bind('click', removeFeed);
	group.find('.add').bind('click', addAnother);
	group.appendTo('#feed_urls');
	
}

function addPANFeed()
{
	var keywords = $("#keyword_input").val().replace(/[^0-9a-zA-Z]/g,",").split(",");
	var url = "http://panfeed.ecs.soton.ac.uk/find/all/" + keywords.join("_");
	
	var group = $('#feed_urls').find('.control-group:first').clone();
	group.find('input').val(url);
	group.find('.remove').bind('click', removeFeed);
	group.find('.add').bind('click', addAnother);
	group.appendTo('#feed_urls');
}
