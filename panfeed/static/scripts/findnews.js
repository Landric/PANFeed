function FindNewsCtrl($scope, $http, $templateCache)
{
    "use strict";
    var documentUrl = URI(document.location);

    $scope.searchTerms = "ecs eprints";
    $scope.searchText = '';
    
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
        if($scope.url === undefined)
        {
            $scope.search();
        }
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

    $scope.fetch = function()
    {
        $http(
        {
            method: "GET",
            url: '/api/v2/feed/?format=json&limit=0',
            cache: $templateCache,
            transformResponse: function(data,headersGetter)
            {
                var objects = JSON.parse(data).objects;
                angular.forEach(objects, function(object)
                {
                    object["searchOn"] = object.title + object.description;
                });
                return objects
            }
        }).success(function(data,status)
        {
            $scope.feeds = arrayShuffle(data);
        });
    }

    /* 
        Modified implementation of Fisher-Yates shuffling algorithm, from:
        http://www.hardcode.nl/subcategory_1/article_317-array-shuffle-function
    */
    function arrayShuffle(oldArray)
    {
        var newArray = oldArray.slice();
        var len = newArray.length;
        var i = len;
        while (i--) 
        {
            var p = parseInt(Math.random()*len);
            var t = newArray[i];
            newArray[i] = newArray[p];
            newArray[p] = t;
        }
        return newArray; 
    }

    $scope.fetch();
}
