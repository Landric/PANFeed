function FindNewsCtrl($scope) {
    $scope.searchTerms = "";
    $scope.url = function() {
        return URI("/find").addSearch({kw: $scope.searchTerms.split(" ")}).toString()
    };
    
}
