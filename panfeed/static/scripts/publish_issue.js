function PublishIssueCtrl($scope)
{
    $scope.items;
    $scope.loading = false;
    $scope.loaded = false;
    
    function addURLsAsItems(from_id, to_id) 
    {
        var issueUrls = $("#"+from_id).val().split("\n");

        // alert(issueUrls[0]);
        $("#"+from_id).val("");

        for(var url in issueUrls)
        {
            // setTimeout stops the ajax hammering the server. django was having a tantrum so i thought this seemed like the simplest fix
            // if anyone has time to work out whats up please let me know
            setTimeout("doAjax('"+issueUrls[url]+"', '"+from_id+"', '"+to_id+"')", url*2000);
        }
    }

    $scope.convertURL = function()
    {
        var converter_url = "/urltoitem";
        jQuery.ajax(
        { 
            url:converter_url,
            data: { url:$scope.url },
            dataType:"json",
            async: false,
            beforeSend: function(xhr, status) 
            {
                $scope.loading = true;
            },
            success: function(data, status,request)
            {
                data.url = $scope.url;
                $scope.item = data;
                $scope.loaded = true;
                $scope.loading = false;
            }
        });
        console.log($scope.item);
    };

    function loadIssueItems(issueid, dom_id)
    {
        jQuery.ajax(
        {
            url:"/issueitems/"+issueid,
            dataType:"json",
            success: function(data, status,request)
            {
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
        $("#"+itemId).parent().slideUp('400', function() 
        {
            $("#"+itemId).parent().remove();
        });
    }

    function changeImg(imgId, urlId)
    {
        $('#'+imgId).attr('src', $('#'+urlId).val());
    }
}
