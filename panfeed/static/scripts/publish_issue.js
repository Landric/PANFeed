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

        var editorial = {'title':$scope.title, 'description':$scope.editorial, 'feed':feed, 'issue_position':0, 'url':'', 'image':''};

        for(var item in $scope.items)
        {
            $scope.items[item].title = $scope.items[item].title + " - " + $scope.title;
            $scope.items[item].issue_position = parseInt(item)+1;
            $scope.items[item].feed = feed;
        }

        var issue = {'title':$scope.title, 'description':$scope.editorial, 'feed':feed};

        publishIssue(issue, editorial, $scope.items);
    };

    function publishIssue(issue, editorial, issue_items)
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
                editorial.special_issue = URI(issue_id).path().toString();

                //var batch_items = [];
                //batch_items.push(editorial);
                publishItem(editorial);

                for(var item in issue_items)
                {
                    issue_items[item].special_issue = URI(issue_id).path().toString();
                    //batch_items.push(issue_items[item]);
                    publishItem(issue_items[item]);
                }

                //publishItems(batch_items);
            }
        });
    }

    function publishItem(item)//s)
    {
        //var objects = {'objects':items};
        $.ajax(
        {
            url: '/api/v2/feeditem/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(item),//objects),
            dataType: 'json',
            processData: false,
            success: function(data, status, request)
            {
                //window.location = "/publishnews";
            }
        });
    }
}
