var app = angular.module('app', ['ngMap']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }]);

app.controller('locatorController', function($scope, $http, $timeout, $location,NgMap, $window) {
  var vm = this;
  var markers = [];
  vm.markers =[];  
  $scope.currentVal= "blog_score";

  NgMap.getMap().then(function(map) {
      vm.map = map;
    });

  vm.showDetail = function(e, marker,index) {
    vm.marker = marker;
    vm.map.showInfoWindow('info', index);
  };

  vm.hideDetail = function() {
    vm.map.hideInfoWindow('info');
  };
  
  $scope.newTab = function(url){    
      $window.open("http://"+url,"_blank")
  }

  $http.get('/api/statistics').then(function(response){
      var data = response.data;      
      angular.forEach(data, function(value) {
        markers.push({
          id:value.blog_id, 
          domain: value.domain,
          pos: [value.latitude, value.longitude],
          blog_score: (value.blog.score*100).toFixed(0),
          apbdes_score: (value.apbdes.score*100).toFixed(0),
          penduduk_score: (value.penduduk.score*100).toFixed(0),
          icon: (value.blog.score*100).toFixed(0)
        })
        vm.markers = markers;
      })        
  });

  $scope.changeContent = function(contentClicked){
    var temp = markers;
    vm.markers = [];
    markers.forEach((value,index) =>{
      temp[index].icon = value;
    });
    vm.markers = temp;
  }  
});
