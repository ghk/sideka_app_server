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
var datasetsDaily = [{
			label: "Berita Harian",
			backgroundColor: fill[1],
			borderColor: fill[1],
			data: [],
			fill: false,
		}, {
			label: "Kependudukan",
			fill: false,
			backgroundColor: fill[2],
			borderColor: fill[2],
			data: [],
		},{
			label: "Keuangan",
			fill: false,
			backgroundColor: fill[3],
			borderColor: fill[3],
			data: [],
		}]

var config = {
	type: 'line',
	data: {
		labels: [],
		datasets: []
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

var canvasDaily = document.getElementById('daily-graph');
var ctxDaily = getCtx(canvasDaily)
config.data.datasets = datasetsDaily;
var chartDaily = new Chart(ctxDaily, config);

var canvasDesa = document.getElementById('desa-graph')
var desaChart = new Chart(getCtx(canvasDesa),config)
var canvasapbdes = document.getElementById('apbdes-graph');
var apbdesChart = new Chart(getCtx(canvasapbdes),config)
var canvasPost = document.getElementById('post-graph');
var postChart = new Chart(getCtx(canvasPost),config)
var canvasPenduduk = document.getElementById('penduduk-graph');
var pendudukChart = new Chart(getCtx(canvasPenduduk),config)


var changeSelected = function(selected){	
	$.getJSON("/api/dashboard?id_supradesa="+selected, function(data){
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

		chartDaily.data.labels = data.daily.label.map(convertDate);
		chartDaily.data.datasets[0].data = data.daily.post;
		chartDaily.data.datasets[1].data = data.daily.penduduk;
		chartDaily.data.datasets[2].data = data.daily.apbdes;	
		chartDaily.update();
	});
}
changeSelected(null);

$('#region-code-select').change(function(){
	var value = $(this).val();
	changeSelected(value);
});

var panelClicked = function(panel_clicked,data){
	switch(panel_clicked){
		case "panel_desa":
			desaChart.data.labels = []
			desaChart.data.datasets = []			
			desaChart.update();	

			for(label in labels()){
				desaChart.data.labels.push(label);	
			}				
			desaChart.data.datasets.push({
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
			desaChart.update();
			desaChart.render();
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
			postChart.data.labels = []
			postChart.data.datasets = []			
			postChart.update();	

			for(label in labels())
				postChart.data.labels.push(label);					
			postChart.data.datasets.push({
				label: "Desa Berberita Seminggu",
				backgroundColor: "#d84315",
				borderColor: "#d84315",
				borderWidth: 1,
				data: dataDashboard["weekly"]["post"].reverse(),			
				fill:false			
			})
			postChart.update();
			postChart.render();
			break;
		case "panel_penduduk":
			pendudukChart.data.labels = []
			pendudukChart.data.datasets = []			
			pendudukChart.update();	

			for(label in labels())
				pendudukChart.data.labels.push(label);					
			pendudukChart.data.datasets.push({
				label: "Desa Berdata Penduduk",
				backgroundColor: "#2196f3",
				borderColor: "#2196f3",
				borderWidth: 1,
				data: dataDashboard["weekly"]["penduduk"].reverse(),
				fill:false						
			})
			pendudukChart.update();
			pendudukChart.render();
			break;
		case "panel_apbdes":
			apbdesChart.data.labels = []
			apbdesChart.data.datasets = []			
			apbdesChart.update();	

			for(label in labels())
				apbdesChart.data.labels.push(label);					
			apbdesChart.data.datasets.push({
				label: "Desa Berdata Keuangan",
				backgroundColor: "#ffa000",
				borderColor: "#ffa000",
				borderWidth: 1,
				data: dataDashboard["weekly"]["apbdes"].reverse(),	
				fill:false					
			})
			apbdesChart.update();
			apbdesChart.render();
			break;
	}	
}

$('[id="panel-graph"]').click(function(){
	var selected = $( "#region-code-select option:selected" ).val();
	var valuePanel = $(this).attr('value');
	if (valuePanel == 'panel_desa'){
		$.getJSON( "/api/domain_weekly?id_supradesa="+selected, function(data){
			panelClicked(valuePanel,data)
		})
	}else{
		panelClicked(valuePanel,"");
	}
});



$.getJSON("/api/supradesa",function(data){
	$("#region-code-select").removeClass("hidden")
	$.each(data, function (i, item) {
		var text;
		if(item.region_code != null || item.region_code != null && item.flag != null){			
			text = item.region_code;
		}else if(item.region_code == null && item.flag != null){			
			text = item.flag;
		}
		$('#region-code-select').append($('<option>', { 
			value: item.id,
			text : text
		}));
	});
});


