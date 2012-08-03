function PublishIssueCtrl($scope)
{
    $scope.items;
    $scope.loading = false;
    $scope.loaded = false;

    $scope.convertURL = function()
    {
        var issue_urls = $scope.urls.split("\n");
        var converter_url = "/urltoitem";

        for(var url in issue_urls)
        {
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
                    $scope.items = $scope.items + data;
                    $scope.loaded = true;
                    $scope.loading = false;
                }
            });
        }
    };

    $scope.fetch = function(issue_id)
    {
        $http(
        {
            method: "GET",
            url: '/api/v2/feeditem/',
            params:
            {
                limit:0,
                special_issue:issue_id,
            },
            cache: $templateCache,
            transformResponse: function(data,headersGetter)
            {
                $scope.loading = true;
                return JSON.parse(data).objects;
            }
        }).success(function(data,status)
        {
            $scope.items = data;
            $scope.loaded = true;
            $scope.loading = false;
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
