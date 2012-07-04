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
	//$('#feed_urls').append("<div class=\"control-group\"><div class=\"controls\"><div class=\"input-append\"><input name=\"url\" type=\"text\" value=\"\"><button class=\"btn remove\" type=\"button\">Remove</button><button class=\"btn add\" type=\"button\">Add another</button></div></div></div>")
	
	$('<button>', {
	'class' : 'btn remove',
	type : 'button',
	text : 'Remove',
	click : removeFeed,
	}).appendTo('#feed_urls');

	$('<button>', {
	'class' : 'btn add',
	type : 'button',
	text : 'Add another',
	click : addAnother,
	}).appendTo('#feed_urls');
}
