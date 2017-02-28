var app = angular.module('app', ['angularUtils.directives.dirPagination']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }]);

app.controller('PostCtrl', function($scope, $http) {
	$scope.currentPage = 1;
	$scope.itemPerPage = 50;
	$scope.totalItems = 0;
	$scope.dataTables = [];
	$scope.headers = ['Domain', 'Score', 'Title','#KBBi','#Kalimat','#Paragraph', '% Gambar Utama','% Title', '% Foto&Caption', '% KBBI', '% Kalimat', '% Paragraph', 'Tanggal']
	var supradesa_id = $( "#select-supradesa option:selected" ).val();
	get_all_post(1, hashUrl())
	
	
	$scope.changePage = function(page) {
		get_all_post(page, supradesa_id)		
	};
 	$scope.formatDate = function(date){           
        return new Date(date);
    };

	$('#select-supradesa').change(function(){	
		var value = $( "#select-supradesa option:selected" ).val();
		get_all_post(1, value);	
		changeUrl(value)	
	});

	function get_all_post(pageBegin, supradesa_id){
		$http.get("/api/count_post_scores?supradesa_id="+supradesa_id).then(function(response){
			$scope.totalItems = parseInt(response.data)
		}); 
		$http.get("/api/post_scores?pagebegin="+pageBegin+"&itemperpage="+$scope.itemPerPage+"&supradesa_id="+supradesa_id).then(function(response){
			$scope.dataTables = response.data;
		}); 
	}

});
