function FindNewsCtrl($scope) {
    $scope.searchTerms = "ecs eprints";
    
    function search(){
        var search = $scope.searchTerms.replace(/,/g,'')
        return {kw: search.split(" ")}
    }
    
    function relativeUrl(){
        return URI("/find").addSearch(search())
    }
    
    $scope.url = function() {
        return relativeUrl().toString();
    };
    
    $scope.absoluteUrl = function() {
        documentUrl = URI(document.location)
        return relativeUrl()
            .authority(documentUrl.authority())
            .scheme(documentUrl.scheme())
            .toString();
    };

    $scope.readerUrl = function() {
        return $scope.absoluteUrl();
    };
    
    $scope.googleReaderURL = function() {
        URL("http://www.google.com/ig/add").addSearch({feedurl:$scope.absoluteUrl()})
    }
}
