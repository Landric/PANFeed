function PublishCtrl($scope)
{
    $scope.item;
    $scope.loading = false;
    $scope.loaded = false;

    $scope.convertURL = function()
    {
        var converter_url = "/urltoitem";
        jQuery.ajax(
        { 
            url:converter_url,
            data: { url:$scope.url },
            dataType:"json",
            async: false,
            beforeSend: function(xhr, status) 
            {
                $scope.loading = true;
            },
            success: function(data, status,request)
            {
                data.url = $scope.url;
                $scope.item = data;
                $scope.loaded = true;
                $scope.loading = false;
            }
        });
        console.log($scope.item);
    };

    $scope.changeImage = function()
    {
        $scope.item.image = $scope.image;
    }
}
