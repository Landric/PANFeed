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
