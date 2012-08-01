function FindNewsCtrl($scope)
{
    $scope.url;
    $scope.searchTerms = "ecs eprints";

    $scope.user = function(link)
    {
        $scope.url = link;
    };

    $scope.search = function()
    {
        var search = $scope.searchTerms.replace(/,/g,'');
        $scope.url = URI("/find").addSearch({kw: search.split(" ")}).toString();
    };
    
    $scope.absoluteUrl = function()
    {
        if($scope.url == undefined)
            $scope.url= $scope.search();
        var documentUrl = URI(document.location);
        return URI($scope.url).authority(documentUrl.authority()).scheme(documentUrl.scheme()).toString();
    };

    $scope.googleReaderUrl = function()
    {
        return URI("http://www.google.com/ig/add").addSearch(
            {
                feedurl:$scope.absoluteUrl()
            }
        ).toString();
    };

    $scope.feedShowReaderUrl = function()
    {
        return URI("http://reader.feedshow.com/subscribe.php").addSearch(
            {
                url:$scope.absoluteUrl()
            }
        ).toString();
    };

    $scope.newsAlloyReaderUrl = function()
    {
        return URI("http://www.newsalloy.com/").addSearch(
            {
                rss:$scope.absoluteUrl()
            }
        ).toString();
    };
}
