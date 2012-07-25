var panfeedModule = angular.module('panfeedModule', []);

panfeedModule.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});
