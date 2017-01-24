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
        labels: content.map(d => convertDate(d.date)),
        datasets: [{
            label: "Berita",
            backgroundColor: chartColors.red,
            borderColor: chartColors.red,
            data: content.map(c => (c.score * 100).toFixed(2)),
            fill: false,
        }
      ]
    },
    options: {
        responsive: true,
	    maintainAspectRatio: false,
        title:{
            display:true,
            text: 'Domain: '+content[0].domain
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        legend: {
            display: false
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

var columns = [
    {
  data: 'date',
  header: 'Tanggal',
	type: 'date',
  dateFormat: 'MM/DD/YYYY',
  correctFormat: true,
    },
		{
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(v => "http://"+v, v => v),
      },
      {
	data: 'title',
	header: 'Judul',
      }, 
      {
	data: 'score',
	header: 'Score',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'kbbi',
	header: '#KBBI',
	type: 'numeric',
      },
      {
	data: 'sentences',
	header: '#kalimat',
	type: 'numeric',
      },
      {
	data: 'paragraphs',
	header: '#Paragraph',
    type: 'numeric',
      },
      {
	data: 'score_thumbnail',
	header: '%Gambar Utama',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'score_title',
	header: '%Judul',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'kbbi_percentage',
	header: '%KBBI',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'score_caption',
	header: '%Foto & Caption',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'score_sentences',
	header: '%Kalimat',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'score_paragraphs',
	header: '%Paragraph',
	type: 'numeric',
	format: '0.00',
      },     
      {
	data: 'date',
	header: 'Tanggal',
      },
    ];
columns.forEach(c => {
	c.readOnly = true;
});

var sortContent = function(){
	var result = content.sort((a,b)=> {
		return new Date(b.date) - new Date(a.date)
	});
	return result
 }
 

window.onload = function() {
    var canvas = document.getElementById('canvas');
    var container = document.getElementById('sheet');
    console.log(content)
    console.log(content.map(c => c.score))

    var hot = new Handsontable(container, {
        data: sortContent(),
        columns: columns,
        columnSorting: true,
        sortIndicator: true,
        rowHeaders: true,
        colHeaders: columns.map(c => c.header),
    });
    setTimeout(()=> hot.render(), 0);

    if (canvas.getContext){
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = 'black';
        ctx.font = '26px Arial';
        ctx.fillText('Quick Brown Fox', 0, 26);
    }
    window.myLine = new Chart(ctx, config);
};
