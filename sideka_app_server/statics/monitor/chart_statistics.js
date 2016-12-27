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
            data: content.map(c => (c.blog.score * 100).toFixed(2)),
            fill: false,
        }, {
            label: "Penduduk",
            fill: false,
            backgroundColor: chartColors.yellow,
            borderColor: chartColors.yellow,
            data: content.map(c => (c.penduduk.score * 100).toFixed(2)),
        },{
          label: "Anggaran",
          fill: false,
          backgroundColor: chartColors.blue,
          borderColor: chartColors.blue,
          data: content.map(c => (c.apbdes.score * 100).toFixed(2)),
        }
      ]
    },
    options: {
        responsive: true,
        title:{
            display:true,
            text:'Chart Statistics'
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
                display: true,
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

window.onload = function() {
  var canvas = document.getElementById('canvas');
  if (canvas.getContext){
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = 'black';
      ctx.font = '26px Arial';
      ctx.fillText('Quick Brown Fox', 0, 26);
  }
    window.myLine = new Chart(ctx, config);
};
