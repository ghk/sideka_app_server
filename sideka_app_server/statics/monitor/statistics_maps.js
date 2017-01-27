var app = angular.module('app', ['ngMap']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }]);

app.controller('locatorController', function($scope, $http, NgMap, $window) {
  var vm = this;
  vm.markers =[];   
      $scope.styles = [
	{ stylers: [
	]},{
	    elementType:'labels',
	    stylers:[
		{visibility:'off'}
	]},{
	    featureType:'water',
	    stylers:[
		{color:'#efefef'}
	]}, {
	    featureType: "landscape",
	    elementType: "all",
	    stylers: [
		{ "color": "#4A9470" }
	]}, {
	    "featureType": "road",
	    "stylers": [
		{ "lightness": 33 }
	]}, {
	    featureType: "administrative.country",
	    elementType: "geometry.stroke",
	    stylers: [
		{ visibility: "on" },
		{ "color": "#000000" }
	]}, {
	    "featureType": "poi",
	    "elementType": "geometry",
	    "stylers": [
		{ "color": "#4A9470" }
	]}
    ];
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
      $window.open(url,"_blank")
  }

  $http.get('/api/statistics').then(function(response){
      var data = response.data;      
      var markers = [];
      for(var i = 0; i < data.length; i++){
	var value = data[i];
        markers.push({
          id:value.blog_id, 
          domain: value.domain,
	      desa: value.domain,
          pos: [value.latitude, value.longitude],
          blog_score: (value.blog.score*100).toFixed(0),
          apbdes_score: (value.apbdes.score*100).toFixed(0),
          penduduk_score: (value.penduduk.score*100).toFixed(0),
          icon: (value.blog.score*100).toFixed(0)
        })
      }
      vm.markers = markers;
  });

  $scope.changeContent = function(contentClicked){
    var temp = vm.markers;
    vm.markers = [];
    temp.forEach(function(value,index){
      temp[index].icon = value[contentClicked];
    });
    vm.markers = temp;
  }  
});
