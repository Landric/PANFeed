function PublishCtrl($scope)
{
    itemCounter = 0;
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
        var itemNum = itemCounter;
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
                    itemCounter++;
                    $('#'+dom_id).append("<div class='item loading'><img src='/static/images/load.gif' alt='' /></div>");
                    var div = $('.item.loading').first();
                    div.removeClass('loading');
                    div.html(renderIssueItem(data[i]));
                }
            }
        });
    }

    function moveUpItem(itemId) 
    {
        var boxToMove = $('#'+itemId).closest('.item');
        var prevBox = boxToMove.prev();

        if(prevBox.length != 0)
        {
            boxToMove.detach();
            boxToMove.insertBefore(prevBox);
            $(window).scrollTop(boxToMove.offset().top);
        }
    }

    function moveDownItem(itemId)
    {
        var boxToMove = $('#'+itemId).closest('.item');
        var nextBox = boxToMove.next();

        if(nextBox.length != 0)
        {
            boxToMove.detach();
            boxToMove.insertAfter(nextBox);
            $(window).scrollTop(boxToMove.offset().top);
        }
    }

    function deleteItem(itemId) 
    {
        $('#'+itemId).closest(".item").slideUp('400', function() {
            $('#'+itemId).closest(".item").remove();
        });
    }

    function changeImg(imgId, urlId){
        $('#'+imgId).attr('src', $('#'+urlId).val());
    }
}
