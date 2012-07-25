function ListFeedsCtrl($scope, $http, $templateCache) {
    $scope.fetch = function(){
    
        $http({
            method: "GET",
            url: '/api/v2/feed/?format=json&limit=0',
            cache: $templateCache,
            transformResponse: function(data,headersGetter){
                return JSON.parse(data).objects;
            }
        }).success(function(data,status){
            $scope.feeds = data;
        });
        
     }
}
