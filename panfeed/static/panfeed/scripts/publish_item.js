function PublishItemCtrl($scope, $http, $templateCache)
{
    "use strict";
    $scope.item;
    $scope.loading = false;
    $scope.loaded = false;

    $scope.convertURL = function()
    {
        var converter_url = django_js_utils.urls.resolve('urltoitem');
        $scope.loading = true;
        jQuery.ajax(
        { 
            url:converter_url,
            data: { url:$scope.url },
            dataType:"json",
            traditional: true,
            success: function(data, status,request)
            {
                $scope.item = data[0];
                $scope.loaded = true;
                $scope.loading = false;
                $('#urls').removeClass('error');
                $scope.$apply();
            },
            error: function(data, status, request)
            {
                $scope.loaded = true;
                $scope.loading = false;
                $('#urls').addClass('error');
                $scope.$apply();
            }
        });
    };

    $scope.fetch = function(item_id)
    {
        $scope.loading = true;
        $http(
        {
            method: "GET",
            url: '/api/v2/feeditem/',
            params:
            {
                limit:1,
                id:item_id,
            },
            cache: $templateCache,
            transformResponse: function(data,headersGetter)
            {
                return JSON.parse(data).objects;
            }
        }).success(function(data,status)
        {
            $scope.item = data[0];
            $scope.loaded = true;
            $scope.loading = false;
            $scope.$apply();
        });
    }
}
