function PublishIssueCtrl($scope)
{
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
        });
     };

    $scope.moveUp = function(itemId)
    {
        if($scope.items[itemId].issuePosition > 1)
        {
            $scope.items[itemId].issuePosition = $scope.items[itemId].issuePosition - 1;
            $scope.items[itemId-1].issuePosition = $scope.items[itemId].issuePosition + 1;
        }
    };

    $scope.moveDown = function(itemId)
    {
        $scope.items[itemId].issuePosition = $scope.items[itemId].issuePosition + 1;
        $scope.items[itemId+1].issuePosition = $scope.items[itemId].issuePosition - 1;
    };

    $scope.remove = function(itemId)
    {
        $scope.items.splice(itemId, 1);
    };
}
