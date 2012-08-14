function PublishIssueCtrl($scope)
{
    $scope.title = '';
    $scope.editorial = '';
    $scope.items;
    $scope.loading = false;
    $scope.loaded = false;

    $scope.convertURLs = function()
    {
        var issue_urls = $scope.urls.split("\n");
        var converter_url = "/urltoitem";
        $scope.loading = true;

        jQuery.ajax(
        { 
            url:converter_url,
            data: { url:issue_urls },
            traditional: true,
            dataType:"json",
            success: function(data, status,request)
            {
                $scope.items = data;
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
        console.log($scope.items[itemId]);
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

        var item = {title:$scope.title, description:$scope.editorial, url:"", image:""};
        $scope.items.unshift(item);

        var issue = publishIssue();

        for(var item in $scope.items)
        {
            $scope.items[item].issue_position = item;
            $scope.items[item].feed = $scope.feed;
            $scope.items[item].special_issue = issue;
            publishIssue($scope.items[item]);
        }
    };

    function publishIssue()
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
                return JSON.parse(data).objects;
            }
        }).success(function(data,status)
        {
            $scope.items = data;
            $scope.loaded = true;
            $scope.loading = false;
        });
    }

    function publishItem(item)
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
                return JSON.parse(data).objects;
            }
        }).success(function(data,status)
        {
            $scope.items = data;
            $scope.loaded = true;
            $scope.loading = false;
        });
    }
}
