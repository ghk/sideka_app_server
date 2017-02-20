var dataDashboard;
var charts = [];

var convertDate = function(date){
  var value = new Date(parseInt(date)*1000)
  var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return value.getDate() + " " + monthNames[value.getMonth()] + " " + value.getFullYear().toString().substr(2,2);
}

var labelsxAxes = function(){
	var result = [];
	for(var i=1;i <= 5;i++){
		result.push('Minggu Ke-'+i)
	}
	return result;
}

var changeSelected = function(selected){	
	if (selected == "") selected = "{}"
	var valueSelected = JSON.parse(selected);
	$.getJSON("/api/dashboard?id_supradesa="+valueSelected, function(data){
		dataDashboard = data;
		var weekly = ["desa", "post", "penduduk", "apbdes"]
		var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
		
		if(charts.length === 0){
			for(var i=0; i<weekly.length; i++){
				var current = weekly[i];
				charts.push($("#weekly-"+current+" .peity").peity("bar", {"fill": [fill[i]]})); 
			}
		}	
		for (var i = 0; i < weekly.length; i++){
			var current = weekly[i];
			var chart =  charts[i];
			
			$("#weekly-"+current+" .count").html(data["weekly"][current][0]);
			$("#weekly-"+current+" .peity").html(data["weekly"][current].reverse().join(","));			
			chart.change();		
		}
		var configDaily = {
			type: 'line',
			data: {
				labels: data.daily.label.map(convertDate),
				datasets: [{
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
				}]
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

		var canvas = document.getElementById('daily-graph');
		if (canvas.getContext){
			var ctx = canvas.getContext('2d');
			ctx.fillStyle = 'black';
			ctx.font = '26px Arial';
			ctx.fillText('Quick Brown Fox', 0, 26);
		}
		new Chart(ctx, configDaily);
	});
}

var panelClicked = function(panel_clicked,data){
	var datasets = [];
	var labelString = "";
	var canvas;
	switch(panel_clicked){
		case "panel_desa":
			canvas = document.getElementById('desa-graph');									
			labelString = 'Jumlah Desa yang terdaftar';								
			datasets.push({
				label: 'Desa Berdomain "sideka.id"',
				backgroundColor: "#8bc34a",
				borderColor: "#8bc34a",
				data: data.sideka_domain.reverse(),
				borderWidth: 1,
			},{
				label: 'Desa Berdomain "desa.id"',
				backgroundColor: "#81D4FA",
				borderColor: "#81D4FA",
				borderWidth: 1,
				data: data.desa_domain.reverse(),
				
			})
			break;
		case "panel_post":
			canvas = document.getElementById('post-graph');
			labelString = 'Jumah Desa Berberita Seminggu';
			datasets.push({
					label: "Desa Berberita Seminggu",
					backgroundColor: "#d84315",
					borderColor: "#d84315",
					borderWidth: 1,
					data: dataDashboard["weekly"]["post"].reverse(),						
			})
			break;
		case "panel_penduduk":
			canvas = document.getElementById('penduduk-graph');
			labelString = 'Jumah Desa Berdata Penduduk';
			datasets.push({
					label: "Desa Berdata Penduduk",
					backgroundColor: "#2196f3",
					borderColor: "#2196f3",
					borderWidth: 1,
					data: dataDashboard["weekly"]["penduduk"].reverse(),						
			})
			break;
		case "panel_apbdes":
			canvas = document.getElementById('apbdes-graph');
			labelString = 'Jumah Desa Berdata Keuangan';
			datasets.push({
					label: "Desa Berdata Keuangan",
					backgroundColor: "#ffa000",
					borderColor: "#ffa000",
					borderWidth: 1,
					data: dataDashboard["weekly"]["apbdes"].reverse(),						
			})
			break;
	}		
	var configPanel = {
		type: 'line',
		data: {
			labels: labelsxAxes(),
			datasets: datasets,
		},
		options: {
			responsive: true,
			maintainAspectRatio:false,
			legend: {
				position: 'top',
			},
			scales: {
				xAxes: [{
					display: false,
				}],
				yAxes: [{
				display: true,
				scaleLabel: {
					display: true,
					labelString: labelString
				}
			}]
			}
		}
	};	
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('Quick Brown Fox', 0, 26);
	}
	new Chart(ctx, configPanel);
}

$('[id="panel-graph"]').click(function(){
	var optionSelected = $( "#region-code-select option:selected" ).val();
	if (optionSelected == "") optionSelected = "{}"
	var valueSelected = JSON.parse(optionSelected);

	var valuePanel = $(this).attr('value');
	if (valuePanel == 'panel_desa'){
		$.getJSON( "/api/domain_weekly?id_supradesa="+valueSelected, function(data){
			panelClicked(valuePanel,data)
		})
	}else{
		panelClicked(valuePanel,"");
	}
});

changeSelected(null);

$.getJSON("/api/supradesa",function(data){
	$("#top_bar").removeClass("hidden")
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

$('#region-code-select').change(function(){
	var value = $(this).val();
	changeSelected(value);
});
