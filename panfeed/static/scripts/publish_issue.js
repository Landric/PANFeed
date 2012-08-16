function PublishIssueCtrl($scope)
{
    $scope.title = '';
    $scope.editorial = '';
    $scope.items = [];
    $scope.loading = false;
    $scope.loaded = false;

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
        $scope.loading = true;
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
            $scope.loaded = true;
            $scope.loading = false;
            $scope.$apply();
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

    $scope.publish = function()
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

        var item = {'title':$scope.title, 'description':$scope.editorial, 'url':'', 'image':''};
        $scope.items.unshift(item);

        for(var item in $scope.items)
        {
            $scope.items[item].issue_position = item;
            $scope.items[item].feed = feed;
        }

        var issue = {'title':$scope.title, 'description':$scope.editorial, 'feed':feed};
        publishIssue(issue, $scope.items);
    };

    function publishIssue(issue, items)
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
                for(var item in $scope.items)
                {
                    $scope.items[item].special_issue = URI(issue_id).path().toString();
                    publishItem($scope.items[item]); //These could be bundled into a single PATCH request if performance becomes an issue. AUTHORIZATION WILL NEED TO BE UPDATED IF YOU DO THIS
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
          processData: false
        });
    }
}
