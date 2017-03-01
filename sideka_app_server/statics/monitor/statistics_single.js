var  chartColors = {
    	red: 'rgb(255, 99, 132)',
    	blue: 'rgb(54, 162, 235)',
    	yellow: 'rgb(255, 205, 86)',
};

var convertDate = function(date){
  var value = new Date(date)
  var monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  return value.getDate() + " " + monthNames[value.getMonth()] + " " + value.getFullYear();
}

var config = {
    type: 'line',
    data: {
        labels: content_daily.map(d => convertDate(d.date)),
        datasets: [{
            label: "Berita",
            backgroundColor: chartColors.red,
            borderColor: chartColors.red,
            data: content_daily.map(c => (c.blog.score * 100).toFixed(2)),
            fill: false,
        }, {
            label: "Penduduk",
            fill: false,
            backgroundColor: chartColors.yellow,
            borderColor: chartColors.yellow,
            data: content_daily.map(c => (c.penduduk.score * 100).toFixed(2)),
        },{
          label: "Anggaran",
          fill: false,
          backgroundColor: chartColors.blue,
          borderColor: chartColors.blue,
          data: content_daily.map(c => (c.apbdes.score * 100).toFixed(2)),
        }
      ]
    },
    options: {
        responsive: true,
	    maintainAspectRatio: false,
        title:{
            display:false,
            text:'Statistik'
        },
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
                    display: true,
                    labelString: 'Date'
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}

var scoreRenderer = function(instance, td, row, col, prop, value, cellProperties) {
	var args = [instance, td, row, col, prop, value * 100, cellProperties];
	var bg = "red";
	var color = "white";
	if (value > 0.4){
		bg = "yellow";
		color = "black";
	}
	if (value > 0.7){
		bg = "green";
		color = "white";
	}

	Handsontable.renderers.NumericRenderer.apply(this, args);
	td.style.backgroundColor = bg;
	td.style.color = color;
};
var convertDate


window.onload = function() {  
    $('#info_desa').text('Desa '+info.desa+', Kecamatan '+info.kecamatan+', Kabupaten '+info.kabupaten)

    var canvas = document.getElementById('canvas');
    if (canvas.getContext){
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = 'black';
        ctx.font = '26px Arial';
        ctx.fillText('Quick Brown Fox', 0, 26);
    }
    window.myLine = new Chart(ctx, config);

    var tbody = $('#table-daily tbody');
    $.each(content_daily,function(idx,content){
        var tr = $('<tr>');
        $('<td>').html('<a href="http://'+content.domain+'">'+content.domain+'</a>').appendTo(tr);
        $('<td>').html(content.blog.score.toFixed(2)).appendTo(tr);
        $('<td>').html(content.penduduk.score.toFixed(2)).appendTo(tr)
        $('<td>').html(content.apbdes.score.toFixed(2)).appendTo(tr)
        $('<td>').html(content.blog.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.blog.score_frequency.toFixed(2)).appendTo(tr)
        $('<td>').html(content.penduduk.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.penduduk.score_quantity.toFixed(2)).appendTo(tr)
        $('<td>').html(content.apbdes.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.apbdes.score_quantity.toFixed(2)).appendTo(tr)
        $('<td>').html(content.blog.last_post).appendTo(tr)
        $('<td>').html(content.blog.count_24h).appendTo(tr)
        $('<td>').html(content.blog.count_1w).appendTo(tr)
        $('<td>').html(content.blog.count_30d).appendTo(tr)
        $('<td>').html(content.penduduk.last_modified).appendTo(tr)
        $('<td>').html(content.penduduk.count).appendTo(tr)
        $('<td>').html(content.apbdes.last_modified).appendTo(tr)
        $('<td>').html(content.apbdes.count).appendTo(tr)
        tbody.append(tr);
    })

    var tbody = $('#table-post tbody');
    $.each(content_post,function(idx,content){
        var tr = $('<tr>');
        $('<td>').html(convertDate(content.date)).appendTo(tr);
        $('<td>').html('<a href="http://'+content.domain+'">'+content.domain+'</a>').appendTo(tr);
        $('<td>').html('<a href="'+content.url+'">'+content.title+'</a>').appendTo(tr)
        $('<td>').html((content.score*100).toFixed(2)).appendTo(tr)
        $('<td>').html(content.kbbi).appendTo(tr)
        $('<td>').html(content.sentences).appendTo(tr)
        $('<td>').html(content.paragraphs).appendTo(tr)
        $('<td>').html((content.score_thumbnail*20)).appendTo(tr)
        $('<td>').html((content.score_title*10).toFixed(2)).appendTo(tr)
        $('<td>').html((content.score_kbbi*20).toFixed(2)).appendTo(tr)
        $('<td>').html((content.score_caption*15).toFixed(2)).appendTo(tr)
        $('<td>').html((content.score_sentences*15).toFixed(2)).appendTo(tr)
        $('<td>').html((content.score_paragraphs*20).toFixed(2)).appendTo(tr)
        tbody.append(tr);
    })
};
