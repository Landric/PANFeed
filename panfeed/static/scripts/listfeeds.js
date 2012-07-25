function ListFeedsCtrl($scope) {
    $scope.get_feeds = function(){
	console.log("OLOLOLOLOL");
        return $.ajax({
                  url: '/api/v2/feed/?format=json&limit=0',
                  type: 'GET',
                  accepts: 'application/json',
                  dataType: 'json'
             }).objects;
     }
}
