document.itemCounter = 0;
function addURLsAsItems(from_id, to_id) {
    var issueUrls = $("#"+from_id).val().split("\n");

//    alert(issueUrls[0]);
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
            $('#'+to_id).append("<div class='item loading'><img src='/static/images/load.gif' alt='' /></div>");
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
    return "<img class='cross' src='/static/images/cross.png' id='item-"+document.itemCounter+"' title='Delete this item' alt='Delete this item' onclick='deleteItem(\"item-"+document.itemCounter+"\")'/>" +
    "<div class='form-field'>URL: <input type='text' name='item-url' value='"+data.url+"'/></div>"+
    "<div class='form-field'>Title: <input type='text' name='item-title' value='"+data.title+"'/></div>" + 
    "<div class='form-field'>Description: <textarea name='item-description'>"+data.description + "</textarea></div>" + 
    "<div class='form-field'>Image URL: <input type='text' id='img-url-"+document.itemCounter+"'  name='item-img' value='" + data.img + "'/> <input type='button' class='img-update' value='Update Image' onclick='changeImg(\"img-"+document.itemCounter+"\", \"img-url-"+document.itemCounter+"\")' /></div>" +
    "<img id='img-"+document.itemCounter+"' src='"+data.img+"' alt='URL does not resolve to image.' /><br />";
}

function addEditorial(url, to_id)
{
	var data = {};
	data.url = url;
	data.title = "Editorial";
	data.description = "";
	data.img = "";
	var div = "<div class='item'>"+renderIssueItem(data)+"</div>";
	$('#'+to_id).append(div);
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
