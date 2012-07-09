document.itemCounter = 0;
function addURLsAsItems(from_id, to_id) {
    var issueUrls = $("#"+from_id).val().split("\n");

    $("#"+from_id).val("");

    for(var url in issueUrls){
        // setTimeout stops the ajax hammering the server. django was having a tantrum so i thought this seemed like the simplest fix
        // if anyone has time to work out whats up please let me know
        setTimeout("doAjax('"+issueUrls[url]+"', '"+from_id+"', '"+to_id+"')", url*2000);
    }

}

function doAjax(url, from_id, to_id){
    var converter_url = "/urltoitem"
    var itemNum = document.itemCounter;
    jQuery.ajax({ 
        url:converter_url,
        data: { url:url },
        dataType:"json",
        async: false,
        beforeSend: function(xhr, status) {
            $('#'+to_id).prepend("<div class='item loading'><img src='/static/images/load.gif' alt='' /></div>");
        },
        success: function(data, status,request){
            data.url = url;
            var div = $('.item.loading').first();
            div.removeClass("loading");
            div.html(renderIssueItem(data));
        }
    });
}

function loadIssueItems(issueid, dom_id)
{
    jQuery.ajax({ 
        url:"/issueitems/"+issueid,
        dataType:"json",
        success: function(data, status,request){
            for(var i=0; i<data.length; i++)
            {
                document.itemCounter++;
                $('#'+dom_id).append("<div class='item loading'><img src='/static/images/load.gif' alt='' /></div>");
                var div = $('.item.loading').first();
                div.removeClass('loading');
                div.html(renderIssueItem(data[i]));
            }
        }
    });

}

function renderIssueItem(data)
{
    document.itemCounter++;

    var buttons = "<div class='control-group'>"+
			"<div class='controls'>"+
				"<div class='btn-group'>"+
					"<button class='btn' id='item-"+document.itemCounter+"' title='Move this item up' alt='Move this item up' onclick='moveItemUp('item-"+document.itemCounter+"')><i class='icon-arrow-up'></i></button>"+
					"<button class='btn' id='item-"+document.itemCounter+"' title='Move this item down' alt='Move this item down' onclick='moveDownItem('item-"+document.itemCounter+"')><i class='icon-arrow-down'></i></button>"+
					"<button class='btn' id='item-"+document.itemCounter+"' title='Delete this item' alt='Delete this item' onclick='deleteItem('item-"+document.itemCounter+"')><i class='icon-trash'></i></button>"+
				"</div>"+
			"</div>"+
		"</div>";

    var url = "<div class='control-group'>"+
			"<label class='control-label'>URL:</label>"+
			"<div class='controls'>"+
				"<input type='text' name='item-url' value='"+data.url+"'/>"+
			"</div>"+
		"</div>";

    var title = "<div class='control-group'>"+
			"<label class='control-label'>Title:</label>"+
			"<div class='controls'>"+
				"<input type='text' name='item-title' value='"+data.title+"'/>"+
			"</div>"+
		"</div>";

    var desc = "<div class='control-group'>"+
			"<label class='control-label'>Description:</label>"+
			"<div class='controls'>"+
				"<textarea name='item-description'>"+data.description + "</textarea>"+
			"</div>"+
		"</div>";

    var image = "<div class='control-group'>"+
			"<label class='control-label'>Image URL:</label>"+
			"<div class='controls'>"+
				"<div class='input-append'>"+
					"<input type='text' id='img-url-"+document.itemCounter+"'  name='item-img' value='" + data.img + "'/><input type='button' class='btn' value='Update Image' onclick='changeImg(\"img-"+document.itemCounter+"\", \"img-url-"+document.itemCounter+"\")' />"+
				"</div>"+
			"</div>"+
		"</div>";

    var preview = "<div class='control-group'>"+
			"<label class='control-label'>Image Preview:</label>"+
			"<div class='controls'>"+
    				"<img id='img-"+document.itemCounter+"' src='"+data.img+"' alt='URL does not resolve to image.' /><br />" +
			"</div>"+
		"</div>";

    var hidden = "<input type='hidden' name='item-ordernumber' value='"+document.itemCounter+"' />";

    return "<div class='well'>" + buttons + url + title + desc + image + preview + hidden + "</div>";
}

function addEditorial(url, to_id)
{
	var data = {};
	data.url = url;
	data.title = "Editorial";
	data.description = "";
	data.img = "";
	var div = "<div class='item'>"+renderIssueItem(data)+"</div>";
	$('#'+to_id).prepend(div);
}

function moveUpItem(itemId) 
{
    var boxToMove = $('#'+itemId).parent();
    var prevBox = boxToMove.prev();
    boxToMove.detach();
    boxToMove.insertBefore(prevBox);
    $(window).scrollTop(boxToMove.offset().top);
}

function moveDownItem(itemId)
{
    var boxToMove = $('#'+itemId).parent();
    var nextBox = boxToMove.next();
    boxToMove.detach();
    boxToMove.insertAfter(nextBox);
    $(window).scrollTop(boxToMove.offset().top);


}

function deleteItem(itemId) 
{
    $("#"+itemId).parent().slideUp('400', function() {
        $("#"+itemId).parent().remove();
    });
}

function changeImg(imgId, urlId){
    $('#'+imgId).attr('src', $('#'+urlId).val());
}
