var dataDashboard, dataStatistics, cachedPanelData = {},cachedDailyGraphData = {}, map, markers = [], chartsPeity = [] ;
var weekly = ["desa", "post", "penduduk", "apbdes"]
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
var width = $(window).width();

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
var mapStyles = [{"featureType":"water","stylers":[{"color":"#19a0d8"}]},{"featureType":"administrative","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"},{"weight":6}]},{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#e85113"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#efe9e4"},{"lightness":-40}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#efe9e4"},{"lightness":-20}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"lightness":100}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"lightness":-100}]},{"featureType":"road.highway","elementType":"labels.icon"},{"featureType":"landscape","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"landscape","stylers":[{"lightness":20},{"color":"#efe9e4"}]},{"featureType":"landscape.man_made","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"labels.text.stroke","stylers":[{"lightness":100}]},{"featureType":"water","elementType":"labels.text.fill","stylers":[{"lightness":-100}]},{"featureType":"poi","elementType":"labels.text.fill","stylers":[{"hue":"#11ff00"}]},{"featureType":"poi","elementType":"labels.text.stroke","stylers":[{"lightness":100}]},{"featureType":"poi","elementType":"labels.icon","stylers":[{"hue":"#4cff00"},{"saturation":58}]},{"featureType":"poi","elementType":"geometry","stylers":[{"visibility":"on"},{"color":"#f0e4d3"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#efe9e4"},{"lightness":-25}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#efe9e4"},{"lightness":-10}]}];
var configPanel = $.extend(true, {}, configDaily);
configPanel.type = "bar";
configPanel.data.labels = getPanelDetailLabels().reverse();
configPanel.options.scales.yAxes[0]["ticks"] ={beginAtZero: true}
configPanel.options.scales.yAxes[0].scaleLabel.labelString = "Jumlah Desa"
delete configPanel.options.scales.xAxes[0]["ticks"]

var canvasDaily = document.getElementById('daily-graph');
var dailyGraph = new Chart(getContext(canvasDaily), configDaily);
var canvasDesa = document.getElementById('desa-graph')
var desaGraph = new Chart(getContext(canvasDesa),configPanel)
var canvasapbdes = document.getElementById('apbdes-graph');
var apbdesGraph = new Chart(getContext(canvasapbdes),configPanel)
var canvasPost = document.getElementById('post-graph');
var postGraph = new Chart(getContext(canvasPost),configPanel)
var canvasPenduduk = document.getElementById('penduduk-graph');
var pendudukGraph = new Chart(getContext(canvasPenduduk),configPanel);
	
function convertDailyGraphDate(data){
	return data.map(function(timestamp, idx){
		if(idx%7 ==0 || idx == (data.length-1)){
			return moment.unix(timestamp).format("DD MMM YYYY");
		}		
		return "";
	});
}

function getPanelDetailLabels (){
	var result = [];
	for(var i=0;i<5;i++){	
		result.push(moment().weekday(i*-7).format("DD MMM YYYY"))
	}
	result[0]="Hari Ini"
	return result;
}

function getContext (canvas){
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('0', 0, 26);
		return ctx
	}
}

function onSupradesaChanged(supradesaId){
	$.getJSON("/api/dashboard?supradesa_id="+supradesaId, function(data){
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

		dailyGraph.data.labels = convertDailyGraphDate(data.daily.label);
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
			
		cachedPanelData = {};	
		onWidthChange(width);
	});
	
	markers= [];
	cachedDailyGraphData = {};
	getStatistics(supradesaId);
	
}

function onPanelClicked(panelName,data){
	var header = ["No","Desa","Domain","Provinsi","Kabupaten","Kecamatan"];
	var thead;
	var tbody;
	switch(panelName){
		case "desa":		
			var newData = $.extend(true, {}, data);
			desaGraph.data.datasets=[];
			desaGraph.update();		

			desaGraph.data.datasets.push({
				label: 'Desa Berdomain "desa.id"',
				type: 'line',
				backgroundColor: "#9900cc",
				borderColor: "#9900cc",
				data: newData.desa_domain.reverse(),
				fill:false
				
			},{
				label: 'Desa Berdomain "sideka.id"',
				type: 'line',
				borderColor: "#ffbb33",
				backgroundColor: "#ffbb33",
				data: newData.sideka_domain.reverse(),
				fill:false
			},{
				label: 'Desa Terdaftar',
				backgroundColor: "#8bc34a",
				borderColor: "#8bc34a",
				borderWidth: 1,
				data: dataDashboard["weekly"]["desa"],
				fill:false
			})
			desaGraph.update();

			var header = ['Minggu','Desa Berdomain "sideka.id"','Desa Berdomain "desa.id"','Desa Terdaftar']			
			var length = data.sideka_domain.length;
			var week = getPanelDetailLabels();
			var tbody = $('#table-domain-weekly tbody')
			var thead = $('#table-domain-weekly thead')	
			applyTableHeader(header,thead);	
			$("tr",tbody).remove();
			$.each(data.sideka_domain, function(idx, content){
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
	if(panelName !=="desa"){
		$("tr",thead).remove() ;
		$("tr",tbody).remove();
		var tr = $('<tr>')
		applyTableHeader(header,thead);
		data[panelName].sort((a,b)=>{return (a.kode > b.kode) ? 1 : ((b.kode > a.kode) ? -1 : 0);})
		$.each(data[panelName],function(idx, content){
			tr = $('<tr>');
			$('<td>').html(idx+1).appendTo(tr);
			$('<td>').append($('<a>').attr("href", "/statistic/"+content.blog_id).text(content.desa)).appendTo(tr);
			$('<td>').append($('<a>').attr("href", "http://"+content.domain).text(content.domain)).appendTo(tr);	
			$('<td>').html(content.propinsi).appendTo(tr);
			$('<td>').html(content.kabupaten).appendTo(tr);					
			$('<td>').html(content.kecamatan).appendTo(tr);
			tbody.append(tr);
		})	
	}
}

// Maps Configuration
function getStatistics(supradesaId){
	initMaps(supradesaId);
	$.getJSON('/api/statistics?supradesa_id='+supradesaId, function(data){
		var icon = "blog";
		dataStatistics = data;
		$.each(data,function(idx,content){
			if(content.latitude != null &&content.longitude)addMarker(content,icon);
		})	
	})
}

function initMaps(supradesaId){
	var center = {lat:-2.604236, lng: 116.499023};
	var zoom = 5
	var errorValue = [0,null]
	$.getJSON( "/api/get_zoom?supradesa_id="+supradesaId, function(data){		
		if(!$.isEmptyObject(data)){
			if(!errorValue.includes(data.latitude)&&!errorValue.includes(data.longitude)){	
				center = {lat:data.latitude, lng:data.longitude};
				zoom = data.zoom;
			}
		}
		map = new google.maps.Map(document.getElementById('map'), {
			zoom: zoom,
			center: center,
			mapTypeControl: false,
			streetViewControl: false,
			styles: mapStyles,
		});	
	})	  
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

	var content = 'Desa: <a href="/statistic/'+content.blog_id+'">'+content.desa+'</a><br />'+
				  'Domain: <a href="http://'+content.domain+'">'+content.domain+'</a><br />'+
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

function onButtonScoreClicked(buttonName){
	clearMarkers();
	$.each(dataStatistics,function(idx, content){
		if(content.latitude != null && content.longitude != null)
			addMarker(content,buttonName);
	})	
	applyTableInMaps(buttonName);
}

function applyTableInMaps(buttonClicked){
	var header= ["No","Score","Desa", "Domain"];
	var thead = $('#table-score-maps thead');
	var tbody = $('#table-score-maps tbody');
	var newData = dataStatistics.sort(function(data1,data2){ return data2[buttonClicked].score - data1[buttonClicked].score})
	var tr = $('<tr>')

	applyTableHeader(header,thead);
	$("tr", tbody).remove();	
	$.each(newData,function(idx, content){
		tr = $('<tr>');
		$('<td>').html(idx+1).appendTo(tr);		
		$('<td>').html(makeButtonScoring(content[buttonClicked].score)).appendTo(tr);
		$('<td>').append($('<a>').attr("href", "/statistic/"+content.blog_id).text(content.desa)).appendTo(tr);
		$('<td>').append($('<a>').attr("href", "/statistic/"+content.blog_id).text(content.domain)).appendTo(tr);
		tbody.append(tr);
	});
}

function clearMarkers() {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

function makeButtonScoring(score){
 	var classButton;
 	var buttonResult;
 	score *=100;
 	
 	if(score < 40)
 		classButton= 'uk-badge uk-badge-danger';
 	else if(score < 70) 
 		classButton ='uk-badge uk-badge-warning'; 
 	else
 		classButton ='uk-badge uk-badge-success';
 	buttonResult = '<span class="'+classButton+'">'+score.toFixed(2)+'</span>';
 	return buttonResult;
}

function applyTableHeader(header,thead){
	var tr = $('<tr>');
	$("tr",thead).remove()
	
	$.each(header,function(idx,content){
		$('<th>').html(content).appendTo(tr);
	})		
	thead.append(tr);
}

function onWidthChange(widthCurrent){	
	if($.isEmptyObject(cachedDailyGraphData))
		cachedDailyGraphData = $.extend(true, {}, dailyGraph.data);

	var startSlice;
	var endSlice =  cachedDailyGraphData.labels.length;

	dailyGraph.data.labels = [];
	dailyGraph.data.datasets = [];
	dailyGraph.update();
	
	if(widthCurrent <= 320)	
		startSlice = cachedDailyGraphData.labels.length - 10;
	else if(widthCurrent > 320 && widthCurrent < 600)		
		startSlice = cachedDailyGraphData.labels.length - 15;			
	else if(widthCurrent >=600 && widthCurrent <=900)	
		startSlice = cachedDailyGraphData.labels.length - 35;					
	else
		startSlice = 0;
	
	dailyGraph.data.labels = cachedDailyGraphData.labels.slice(startSlice,endSlice)
	$.each(cachedDailyGraphData.datasets,function(idx,dataset){
		var temp = $.extend(true, {}, dataset)
		temp.data = temp.data.slice(startSlice,endSlice)
		dailyGraph.data.datasets.push(temp)
	})	
	dailyGraph.update();
}

$('#button-score button').click(function(){
	var value = $(this).val();
	onButtonScoreClicked(value)
})

$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeUrl(value)	
	onSupradesaChanged(value)
});

$('.switch-score select').change(function(){
	var value = $(this).val();
	onButtonScoreClicked(value)
});

$('#fullscreen-maps').click(function(){
	var buttonActive = $("#button-score .uk-active" ).val();
	applyTableInMaps(buttonActive);
});

$('[id="panel-graph"]').click(function(){
	var supradesaId = $( "#select-supradesa option:selected").val();
	var panelName = $(this).attr('data-panel-name');
	if (panelName == 'desa'){
		$.getJSON( "/api/domain_weekly?supradesa_id="+supradesaId, function(data){
			onPanelClicked(panelName, data);
		})
	}else{
		if($.isEmptyObject(cachedPanelData)){
			$.getJSON( "/api/panel_weekly?supradesa_id="+supradesaId, function(data){
				cachedPanelData = data;
				onPanelClicked(panelName,data);
			})
		}else{
			onPanelClicked(panelName, cachedPanelData);
		}
	}
});


$(window).on('resize', function(){
	if($(this).width() != width){
		width = $(this).width();
		onWidthChange(width);		
	}
});

window.onload = function(){
	onSupradesaChanged(hashUrl());
}

