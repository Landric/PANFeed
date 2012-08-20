function PublishIssueCtrl($scope, $http, $templateCache)
{
    $scope.title = '';
    $scope.editorial = '';
    $scope.items = [];
    $scope.loading = false;
    $scope.loaded = false;
    var submitted_items = 0;
    var deleted_items = 0;
    var id = 0;


    $scope.convertURLs = function()
    {
        var issue_urls = $scope.urls.split("\n");
        var converter_url = "/urltoitem";
        $scope.loading = true;

        $.ajax(
        { 
            url:converter_url,
            data: { url:issue_urls },
            traditional: true,
            dataType:"json",
            success: function(data, status, request)
            {
                $scope.items = $scope.items.concat(data);
                $scope.loaded = true;
                $scope.loading = false;
                $scope.$apply();
            }
        });
    };

    $scope.fetch = function(issue_id)
    {
        id = issue_id;

        $scope.loading = true;
        $http(
        {
            method: "GET",
            url: '/api/v2/specialissue/',
            params:
            {
                limit:1,
                id:issue_id,
            },
            cache: $templateCache,
            transformResponse: function(data,headersGetter)
            {
                return JSON.parse(data).objects;
            }
        }).success(function(data,status)
        {
            $scope.title = data[0].title;
            $scope.editorial = data[0].description;
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
                    return JSON.parse(data).objects;
                }
            }).success(function(data,status)
            {
                $scope.items = data;
                $scope.original_items = data;
                $scope.loaded = true;
                $scope.loading = false;
                $scope.$apply();
            });
        });
     };

    $scope.moveUp = function(itemId)
    {
        if(itemId > 0)
        {
            var item = $scope.items[itemId];
            $scope.items[itemId] = $scope.items[itemId-1];
            $scope.items[itemId-1] = item;
        }
    };

    $scope.moveDown = function(itemId)
    {
        if(itemId < $scope.items.length-1)
        {
            var item = $scope.items[itemId];
            $scope.items[itemId] = $scope.items[itemId+1];
            $scope.items[itemId+1] = item;
        }
    };

    $scope.remove = function(itemId)
    {
        $scope.items.splice(itemId, 1);
    };

    $scope.publish = function(update)
    {
        if($scope.title == '')
        {
            alert("Need a title");
        }
        if($scope.editorial == '')
        {
            alert("Need a description");
        }
        if($scope.items.length == 0)
        {
            alert("Need items");
        }

        var feed = '/api/v2/feed/'.concat($scope.feed, '/');

        for(var item in $scope.items)
        {
            $scope.items[item].issue_position = parseInt(item)+1;
            $scope.items[item].feed = feed;
        }

        var issue = {'title':$scope.title, 'description':$scope.editorial, 'feed':feed};

        if(update)
        {
           removeItems(issue, $scope.original_items, $scope.items);
        }
        else
        {
           publishIssue(issue, $scope.items);
        }
    };

    function removeItems(issue, original_items, issue_items)
    {
        deleted_items = original_items.length;
        for(var item in original_items)
        {
            $.ajax(
            {
                url: original_items[item].resource_uri,
                type: 'DELETE',
                contentType: 'application/json',
                dataType: 'json',
                processData: false,
                success: function(data, status, request)
                {
                    deleted_items = deleted_items - 1;
                    if (deleted_items == 0)
                    {
                      updateIssue(issue, issue_items)  
                    }
                }
            });
        }
    }

    function updateIssue(issue, issue_items)
    {
        $.ajax(
        {
            url: '/api/v2/specialissue/'+id,
            type: 'PUT',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(issue),
            processData: false,
            success: function(data, status, request)
            {
                var issue_id = '/api/v2/specialissue/'+id
                submitted_items = issue_items.length;
                for(var item in issue_items)
                {
                    issue_items[item].special_issue = issue_id;
                    publishItem(issue_items[item]);
                }
            }
        });
    }

    function publishIssue(issue, issue_items)
    {
        $.ajax(
        {
            url: '/api/v2/specialissue/',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(issue),
            processData: false,
            success: function(data, status, request)
            {
                var issue_id =  request.getResponseHeader("Location");

                submitted_items = issue_items.length;
                for(var item in issue_items)
                {
                    issue_items[item].special_issue = URI(issue_id).path().toString();
                    publishItem(issue_items[item]);
                }
            }
        });
    }

    function publishItem(item)
    {
        $.ajax(
        {
            url: '/api/v2/feeditem/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(item),
            dataType: 'json',
            processData: false,
            success: function(data, status, request)
            {
                submitted_items = submitted_items - 1;
                if (submitted_items == 0)
                {
                    window.location = "/publishnews";
                }
            }
        });
    }
}
