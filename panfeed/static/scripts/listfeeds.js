function ListFeedsCtrl($scope, $http, $templateCache) 
{
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
            $scope.feeds = data;
        });
     }
     
     $scope.fetch();
}
