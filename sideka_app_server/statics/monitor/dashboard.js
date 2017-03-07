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
		display: true,
		ticks: {
		autoSkip: false,
		maxRotation: 0,
		minRotation: 0
		}			
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

var dataDashboard, dataStatistics, dataPanel = {}, map, markers = [], chartsPeity = [] ;
var weekly = ["desa", "post", "penduduk", "apbdes"]
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
var canvasDaily = document.getElementById('daily-graph');
var dailyGraph = new Chart(getCtx(canvasDaily), configDaily);
var canvasDesa = document.getElementById('desa-graph')
var desaGraph = new Chart(getCtx(canvasDesa),configPanel)
var canvasapbdes = document.getElementById('apbdes-graph');
var apbdesGraph = new Chart(getCtx(canvasapbdes),configPanel)
var canvasPost = document.getElementById('post-graph');
var postGraph = new Chart(getCtx(canvasPost),configPanel)
var canvasPenduduk = document.getElementById('penduduk-graph');
var pendudukGraph = new Chart(getCtx(canvasPenduduk),configPanel);
	
function convertDate(data){
	results = []
	$.each(data,function(idx,timestamp){
		results.push("")
		if(idx%7 ==0 || idx == (data.length-1)){
			results[idx] = (moment.unix(timestamp).format("DD MMM YYYY"));
		}		
	})
	return results
}

function labels (){
	var result = [];
	for(var i=0;i<5;i++){	
		result.push(moment().weekday(i*-7).format("DD MMM YYYY"))
	}
	result[0]="Hari Ini"
	return result.reverse();
}

function getCtx (canvas){
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('0', 0, 26);
		return ctx
	}
}

function changeSelected(supradesa_id){
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

function panelClicked(panel_clicked,data){
	var header = ["No","Domain", "Desa", "Kecamatan", "Kabupaten","Provinsi"]
	var thead;
	var tbody;
	switch(panel_clicked){
		case "desa":		
			desaGraph.data.datasets=[];
			desaGraph.update();		

			desaGraph.data.datasets.push({
				label: 'Desa Terdaftar',
				backgroundColor: "#8bc34a",
				borderColor: "#8bc34a",
				borderWidth: 1,
				data: dataDashboard["weekly"]["desa"],
				fill:false
				
			},{
				label: 'Desa Berdomain "desa.id"',
				backgroundColor: "#9900cc",
				borderColor: "#9900cc",
				borderWidth: 1,
				data: data.desa_domain,
				fill:false
				
			},{
				label: 'Desa Berdomain "sideka.id"',
				backgroundColor: "#ffbb33",
				borderColor: "#ffbb33",
				data: data.sideka_domain,
				borderWidth: 1,
				fill:false
			})
			desaGraph.update();
			desaGraph.render();
			tbody = $('#table-domain-weekly tbody');
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
		case "post":
			postGraph.data.datasets = []			
			postGraph.update();								
			postGraph.data.datasets.push({
				label: "Desa Berberita Seminggu",
				backgroundColor: "#d84315",
				borderColor: "#d84315",
				borderWidth: 1,
				data: dataDashboard["weekly"]["post"],			
				fill:false			
			})
			postGraph.update();
			thead = $('#table-post-weekly thead');
			tbody = $('#table-post-weekly tbody');
			break;
		case "penduduk":
			pendudukGraph.data.datasets = []			
			pendudukGraph.update();					
			pendudukGraph.data.datasets.push({
				label: "Desa Berdata Penduduk",
				backgroundColor: "#2196f3",
				borderColor: "#2196f3",
				borderWidth: 1,
				data: dataDashboard["weekly"]["penduduk"],
				fill:false						
			})
			pendudukGraph.update();
			thead = $('#table-penduduk-weekly thead');
			tbody = $('#table-penduduk-weekly tbody');
			break;
		case "apbdes":
			apbdesGraph.data.datasets = []			
			apbdesGraph.update();						
			apbdesGraph.data.datasets.push({
				label: "Desa Berdata Keuangan",
				backgroundColor: "#ffa000",
				borderColor: "#ffa000",
				borderWidth: 1,
				data: dataDashboard["weekly"]["apbdes"],	
				fill:false					
			})
			apbdesGraph.update();
			thead = $('#table-apbdes-weekly thead');
			tbody = $('#table-apbdes-weekly tbody');
			break;
	}	
	if(panel_clicked !=="desa"){
		$("tr",thead).remove();
		$("tr",tbody).remove();
		var tr = $('<tr>')
		$.each(header,function(idx,content){
			$('<th>').html(content).appendTo(tr);
		})		
		thead.append(tr);	

		$.each(data[panel_clicked],function(idx, content){
			tr = $('<tr>');
			$('<td>').html(idx+1).appendTo(tr);
			$('<td>').append($('<a>').attr("href", content.url).text(content.domain)).appendTo(tr);
			$('<td>').html(content.desa).appendTo(tr);
			$('<td>').html(content.kecamatan).appendTo(tr);
			$('<td>').html(content.kabupaten).appendTo(tr);
			$('<td>').html(content.propinsi).appendTo(tr);
			tbody.append(tr);
		})	
	}
}

// Maps Configuration
function getStatistics(supradesa_id){
	initMaps();
	$.getJSON('/api/statistics?supradesa_id='+supradesa_id, function(data){
		var icon = "blog";
		dataStatistics = data;	
		$.each(data,function(idx,content){
			if(content.latitude != null &&content.longitude)addMarker(content,icon);
		})	
	})
}

function initMaps(){
	var center = {lat:-2.604236, lng: 116.499023};
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 5,
		center: center,
		mapTypeId: google.maps.MapTypeId.TERRAIN
	});	  
}

function addMarker(content,icon) {
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

function buttonScoreClicked(clicked){
	clearMarkers();
	$.each(dataStatistics,function(idx, content){
		if(content.latitude != null && content.longitude != null)addMarker(content,clicked);
	})
	
}

function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

function clearMarkers() {
  setMapOnAll(null);
}

function deleteMarkers() {
  clearMarkers();
  markers = [];
}

$('#button-score button').click(function(){
	var value = $(this).val();
	buttonScoreClicked(value)
})

$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
	changeUrl(value)
	deleteMarkers();	
	getStatistics(hashUrl())
	dataPanel = {};
});

$('[id="panel-graph"]').click(function(){
	var selected = $( "#select-supradesa option:selected" ).val();
	var valuePanel = $(this).attr('value');
	if (valuePanel == 'desa'){
		$.getJSON( "/api/domain_weekly?supradesa_id="+selected, function(data){
			panelClicked(valuePanel,data)
		})
	}else{
		if($.isEmptyObject(dataPanel)){
			$.getJSON( "/api/panel_weekly?supradesa_id="+selected, function(data){
				dataPanel = data;
				panelClicked(valuePanel,data)
			})
		}else{
			panelClicked(valuePanel,dataPanel)
		}
	}
});

window.onload = function(){
	changeSelected(hashUrl())
	getStatistics(hashUrl())
}