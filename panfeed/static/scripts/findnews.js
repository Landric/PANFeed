function FindNewsCtrl($scope) {
    $scope.searchTerms = "ecs eprints";
    
    function search(){
        var search = $scope.searchTerms.replace(/,/g,'');
        return {kw: search.split(" ")};
    }
    
    $scope.url = function() {
        return URI("/find").addSearch(search()).toString();
    };
    
    $scope.absoluteUrl = function() {
        var documentUrl = URI(document.location);
        return URI($scope.url()).authority(documentUrl.authority()).scheme(documentUrl.scheme());
    };

    $scope.googleReaderUrl = function() {
        return URI("http://www.google.com/ig/add").addSearch(
            {
                feedurl:$scope.absoluteUrl()
            }
        ).toString();
    }

    $scope.feedShowReaderUrl = function() {
        return URI("http://reader.feedshow.com/subscribe.php").addSearch(
            {
                url:$scope.absoluteUrl()
            }
        ).toString();
    }

    $scope.newsAlloyReaderUrl = function() {
        return URI("http://www.newsalloy.com/").addSearch(
            {
                rss:$scope.absoluteUrl()
            }
        ).toString();
    }

}
