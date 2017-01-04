var app = angular.module('app', ['ngMap']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }]);

app.controller('locatorController', function($scope, $http, $timeout, $location) {
  var ctrl = this;
  ctrl.markers =[];
  $scope.contentSelected = "blog_score";  

  $http.get('/api/statistics').then(function(response){
      var data = response.data;      
      angular.forEach(data, function(value) {
        ctrl.markers.push({
          id:value.blog_id, 
          domain: value.domain,
          pos: [value.latitude, value.longitude],
          blog_score: (value.blog.score*100).toFixed(0),
          apbdes_score: (value.apbdes.score*100).toFixed(0),
          penduduk_score: (value.penduduk.score*100).toFixed(0),
          icon: (value.blog.score*100).toFixed(0)
        })
      })        
  });
  
  $scope.changeContent = function(contentSelected){
    var score;
    var thisCtrl = ctrl.markers;
    ctrl.markers = [];

    score = thisCtrl.map(p => p.icon =p[contentSelected]);
    score.forEach((value,index) =>{
      thisCtrl[index].icon = value;
    });
    ctrl.markers = thisCtrl;
    return
    
  }  

});
