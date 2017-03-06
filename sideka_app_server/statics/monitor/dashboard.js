var dataDashboard, chartsPeity = [];
var map, markers = [], dataStatistics;
var weekly = ["desa", "post", "penduduk", "apbdes"]
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];

var convertDate = function(data){
	results = []
	$.each(data,function(idx,timestamp){
		results.push("")
		if(idx%7 ==0 || idx == (data.length-1)){
			results[idx] = (moment.unix(timestamp).format("DD MMM YYYY"));
		}		
	})
	return results
}

var labels = function(){
	var result = [];
	for(var i=0;i<5;i++){	
		result.push(moment().weekday(i*-7).format("DD MMM YYYY"))
	}
	result[0]=moment().format('[Hari ini,] dddd');
	return result.reverse();
}

var getCtx = function(canvas){
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('0', 0, 26);
		return ctx
	}
}

var configDaily = {
	type: 'line',
	data: {
		labels: [],
		datasets: [],
	},
	options: {
	responsive: true,
	maintainAspectRatio:false,
	tooltips: {
		position: 'nearest',
		mode: 'index',
		intersect: false,
	},
	hover: {
		mode: 'nearest',
		intersect: true
	}, 
	scales: {
		xAxes: [{
		display: true			
		}],
		yAxes: [{
		display: true,
		scaleLabel: {
			display: true,
			labelString: '#Aktifitas'
		}
		}]
	}
	}
};
var configPanel = {
	type: 'line',
	data: {
		labels: labels(),
		datasets: [],
	},
	options: {
	responsive: true,
	maintainAspectRatio:false,
	tooltips: {
		position: 'nearest',
		mode: 'index',
		intersect: false,
	},
	hover: {
		mode: 'nearest',
		intersect: true
	}, 
	scales: {
		xAxes: [{
			display: true,
			scaleLabel: {
				display: true,
			}
		}],
		yAxes: [{
		ticks: {
			beginAtZero: true
		},
		display: true,
		scaleLabel: {
			display: true,
			labelString: 'Jumlah Desa'
		}
		}]
	}
	}
};

var canvasDaily = document.getElementById('daily-graph');
var dailyGraph = new Chart(getCtx(canvasDaily), configDaily);
var canvasDesa = document.getElementById('desa-graph')
var desaGraph = new Chart(getCtx(canvasDesa),configPanel)
var canvasapbdes = document.getElementById('apbdes-graph');
var apbdesGraph = new Chart(getCtx(canvasapbdes),configPanel)
var canvasPost = document.getElementById('post-graph');
var postGraph = new Chart(getCtx(canvasPost),configPanel)
var canvasPenduduk = document.getElementById('penduduk-graph');
var pendudukGraph = new Chart(getCtx(canvasPenduduk),configPanel)

var changeSelected = function(supradesa_id){
	$.getJSON("/api/dashboard?supradesa_id="+supradesa_id, function(data){
		dataDashboard = data;	
		if(chartsPeity.length === 0){
			for(var i=0; i<weekly.length; i++){
				var current = weekly[i];
				chartsPeity.push($("#weekly-"+current+" .peity").peity("bar", {"fill": [fill[i]]})); 
			}
		}	
		for (var i = 0; i < weekly.length; i++){
			var current = weekly[i];
			var chart =  chartsPeity[i];
			
			$("#weekly-"+current+" .count").html(data["weekly"][current][0]);
			$("#weekly-"+current+" .peity").html(data["weekly"][current].reverse().join(","));			
			chart.change();		
		}
		dailyGraph.data.labels =[];
		dailyGraph.data.datasets = [];
		dailyGraph.update();

		dailyGraph.data.labels = convertDate(data.daily.label);
		dailyGraph.data.datasets.push({
				label: "Berita Harian",
				backgroundColor: fill[1],
				borderColor: fill[1],
				data: data.daily.post,
				fill: false,
			}, {
				label: "Kependudukan",
				fill: false,
				backgroundColor: fill[2],
				borderColor: fill[2],
				data: data.daily.penduduk,
			},{
				label: "Keuangan",
				fill: false,
				backgroundColor: fill[3],
				borderColor: fill[3],
				data: data.daily.apbdes,
			})
		dailyGraph.update();
	});
}

var panelClicked = function(panel_clicked,data){
	switch(panel_clicked){
		case "panel_desa":		
			desaGraph.data.datasets=[]	
			desaGraph.update();				
			desaGraph.data.datasets.push({
				label: 'Desa Berdomain "sideka.id"',
				backgroundColor: "#8bc34a",
				borderColor: "#8bc34a",
				data: data.sideka_domain,
				borderWidth: 1,
				fill:false
			},{
				label: 'Desa Berdomain "desa.id"',
				backgroundColor: "#81D4FA",
				borderColor: "#81D4FA",
				borderWidth: 1,
				data: data.desa_domain,
				fill:false
				
			})
			desaGraph.update();
			var tbody = $('#table-domain-weekly tbody');
			var week = labels().reverse();
			$("tr",tbody).remove();

			$.each(data.sideka_domain,function(idx,content){
				var tr = $('<tr>');
				$('<td>').html(week[idx]).appendTo(tr)
				$('<td>').html(data.sideka_domain[idx]).appendTo(tr)
				$('<td>').html(data.desa_domain[idx]).appendTo(tr)
				$('<td>').html(parseInt(data.sideka_domain[idx])+parseInt(data.desa_domain[idx])).appendTo(tr)
				tbody.append(tr);
			})
			break;
		case "panel_post":
			postGraph.data.datasets = []			
			postGraph.update();	
							
			postGraph.data.datasets.push({
				label: "Desa Berberita Seminggu",
				backgroundColor: "#d84315",
				borderColor: "#d84315",
				borderWidth: 1,
				data: dataDashboard["weekly"]["post"].reverse(),			
				fill:false			
			})
			postGraph.update();
			break;
		case "panel_penduduk":
			pendudukGraph.data.datasets = []			
			pendudukGraph.update();					
			pendudukGraph.data.datasets.push({
				label: "Desa Berdata Penduduk",
				backgroundColor: "#2196f3",
				borderColor: "#2196f3",
				borderWidth: 1,
				data: dataDashboard["weekly"]["penduduk"].reverse(),
				fill:false						
			})
			pendudukGraph.update();
			break;
		case "panel_apbdes":
			apbdesGraph.data.datasets = []			
			apbdesGraph.update();						
			apbdesGraph.data.datasets.push({
				label: "Desa Berdata Keuangan",
				backgroundColor: "#ffa000",
				borderColor: "#ffa000",
				borderWidth: 1,
				data: dataDashboard["weekly"]["apbdes"].reverse(),	
				fill:false					
			})
			apbdesGraph.update();
			break;
	}	
}

$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
	changeUrl(value)
	deleteMarkers();	
	getStatistics(hashUrl())
});

$('[id="panel-graph"]').click(function(){
	var selected = $( "#select-supradesa option:selected" ).val();
	var valuePanel = $(this).attr('value');
	if (valuePanel == 'panel_desa'){
		$.getJSON( "/api/domain_weekly?supradesa_id="+selected, function(data){
			panelClicked(valuePanel,data)
		})
	}else{
		panelClicked(valuePanel,"");
	}
});



// Maps Configuration
var getStatistics = function(supradesa_id){
	initMaps();
	$.getJSON('/api/statistics?supradesa_id='+supradesa_id, function(data){
		var icon = "blog";
		dataStatistics = data;	
		$.each(data,function(idx,content){
			if(content.latitude != null &&content.longitude)addMarker(content,icon);
		})	
	})
}

var initMaps = function(){
	var center = {lat:-2.604236, lng: 116.499023};
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 5,
		center: center,
		mapTypeId: google.maps.MapTypeId.TERRAIN
	});	  
}

var addMarker = function (content,icon) {
	var host = window.location.origin;
	var pathImage = "/statics/content/icons/number/number_"+(content[icon].score*100).toFixed()+".png"
	var loc = {lat: content.latitude,lng:content.longitude}
	var marker = new google.maps.Marker({
		position: loc,
		map: map,
		icon: host+pathImage
	});

	var content = 'Domain: <a href="http://'+content.domain+'">'+content.domain+'</a><br />'+
				  'Berita: '+(content.blog.score*100).toFixed(2)+'<br />'+
				  'Kependudukan: '+(content.penduduk.score*100).toFixed(2)+'<br />'+
				  'Apbdes: '+(content.apbdes.score*100).toFixed(2);
	var infowindow = new google.maps.InfoWindow();
	google.maps.event.addListener(marker,'click', (function(marker,content,infowindow){
		return function() {
			infowindow.setContent(content);
			infowindow.open(map,marker);
		};
	})(marker,content,infowindow));
	markers.push(marker);
}

var buttonScoreClicked = function(clicked){
	clearMarkers();
	$.each(dataStatistics,function(idx, content){
		if(content.latitude != null && content.longitude != null)addMarker(content,clicked);
	})
	
}

$('#button-score button').click(function(){
	var value = $(this).val();
	buttonScoreClicked(value)
})

var setMapOnAll = function(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

var clearMarkers = function() {
  setMapOnAll(null);
}

// Shows any markers currently in the array.
var showMarkers =function() {
  setMapOnAll(map);
}

var deleteMarkers =function() {
  clearMarkers();
  markers = [];
}

window.onload = function(){
	changeSelected(hashUrl())
	getStatistics(hashUrl())
}