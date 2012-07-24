function FindNewsCtrl($scope) {
    $scope.searchTerms = "ecs eprints";
    $scope.url = function() {
        var search = $scope.searchTerms.replace(/,/g,'');
        return URI("/find").addSearch({kw: search.split(" ")}).toString();
    };
    
    $scope.absoluteUrl = function() {
        return URI(document.location).path($scope.url()).toString().replace(/http::/g,'http:');
    };

    $scope.readerUrl = function() {
        return URI(document.location).path($scope.url()).toString().replace(/http::/g,'http%3A');
    };
}
