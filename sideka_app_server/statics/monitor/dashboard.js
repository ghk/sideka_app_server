var convertDate = function(date){
  var value = new Date(parseInt(date)*1000)
  var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return value.getDate() + " " + monthNames[value.getMonth()] + " " + value.getFullYear().toString().substr(2,2);
}

var labels = function(){
	var result = [];
	for(var i=1;i <= 5;i++){
		result.push('Minggu Ke-'+i)
	}
	return result;
}

var getCtx = function(canvas){
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('Quick Brown Fox', 0, 26);
		return ctx
	}
}

var dataDashboard, chartsPeity = [];
var weekly = ["desa", "post", "penduduk", "apbdes"]
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
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
		display: false			
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
		display: false			
		}],
		yAxes: [{
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

var changeSelected = function(selected){	
	if(!selected)selected = null;
	$.getJSON("/api/dashboard?supradesa_id="+selected, function(data){
		dataDashboard = data;		
		console.log(data)
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

		dailyGraph.data.labels = data.daily.label.map(convertDate);
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
changeSelected(null);

$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value);
});

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
			$.each(data.sideka_domain,function(idx,content){
				var tr = $('<tr>');
				$('<td>').html(idx+1).appendTo(tr)
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

$.getJSON("/api/supradesa",function(data){
	$("#select-supradesa").removeClass("hidden")
	$.each(data, function (i, item) {
		var text;
		if(item.region_code != null || item.region_code != null && item.flag != null){			
			text = item.region_code;
		}else if(item.region_code == null && item.flag != null){			
			text = item.flag;
		}
		$('#select-supradesa').append($('<option>', { 
			value: item.id,
			text : text
		}));
	});
});


