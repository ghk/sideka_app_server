var convertDate = function(date){
  var value = new Date(parseInt(date)*1000)
  var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return value.getDate() + " " + monthNames[value.getMonth()] + " " + value.getFullYear().toString().substr(2,2);
}

$("#weekly-desa").click(function(){
	$.getJSON( "/api/panel_desa", function(data){
		console.log(data)
		var config_daily = {
	    type: 'bar',
	    data: {
		labels: [1,2,3,4,5],
		datasets: [{
		    label: "Desa Ber-domain Sideka.id",
		    backgroundColor: "#8bc34a",
		    borderColor: "#8bc34a",
		    data: data.sideka_domain,
		    fill: false,
		},{
			label: "Desa Ber-domain desa.id",
		    backgroundColor: "#d84315",
		    borderColor: "#d84315",
		    data: data.desa_domain,
		    fill: false,
			
		}]
	    },
	    options: {
		responsive: true,
		maintainAspectRatio:false,
		tooltips: {
			mode: 'index',
			intersect: false,
		},
		hover: {
		    mode: 'nearest',
		    intersect: true
		},
		scales: {
		    xAxes: [{
			display: false,
			scaleLabel: {
			    display: false,
			    labelString: 'Tanggal'
			}
		    }],
		    yAxes: [{
			display: true,
			scaleLabel: {
			    display: true,
			    labelString: 'Jumlah Desa yang terdaftar'
			}
		    }]
		}
	    }
	};

	var canvas = document.getElementById('desa-graph');

	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('Quick Brown Fox', 0, 26);
	}
	new Chart(ctx, config_daily);
	});
});

$.getJSON("/api/dashboard", function(data){
	var weekly = ["desa", "post", "penduduk", "apbdes"]
	var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
	for (var i = 0; i < weekly.length; i++){
		var current = weekly[i];
		$("#weekly-"+current+" .count").html(data["weekly"][current][0]);
		$("#weekly-"+current+" .peity").html(data["weekly"][current].reverse().join(","));
		$("#weekly-"+current+" .peity").peity("bar", {"fill": [fill[i]]});
	}
	var config_daily = {
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
		}
	      ]
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
			display: false,
			scaleLabel: {
			    display: false,
			    labelString: 'Tanggal'
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

	var canvas = document.getElementById('daily-graph');

	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('Quick Brown Fox', 0, 26);
	}
	new Chart(ctx, config_daily);
});
