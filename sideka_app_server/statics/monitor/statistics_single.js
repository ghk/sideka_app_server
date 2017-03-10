contentDataQuality = contentDataQuality.filter(c=> c.date !=="None")
//if(contentDataQuality.length >=63)contentDataQuality = contentDataQuality.slice((contentDataQuality.length-63),contentDataQuality.length)
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
var width = $(window).width();
var cachedDataQualityGraph={};
var config= {
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
				labelString: 'Kualitas Data'
			},
            ticks:{
                beginAtZero:true
            }
		}]
	}
	}
};
var canvasDataQuality = document.getElementById('data-quality-graph');
var dataQualityGraph = new Chart(getContext(canvasDataQuality), config);
    
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
function convertGraphDate(data){
	return data.map(function(content, idx){
		if(idx%7 ==0){
			return moment(content.date).format("DD MMM YYYY");
		}		
		return "";
	});
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
function applyGraph(){
    dataQualityGraph.data.labels = convertGraphDate(contentDataQuality)
    dataQualityGraph.data.datasets.push({
        label: "Berita",
        backgroundColor: fill[1],
        borderColor: fill[1],
        data: contentDataQuality.map(c => (c.blog.score * 100).toFixed(2)),
        fill: false,
    }, {
        label: "Penduduk",       
        backgroundColor: fill[2],
        borderColor: fill[2],
        data: contentDataQuality.map(c => (c.penduduk.score * 100).toFixed(2)),
        fill: false,
    },{
        label: "Anggaran",
        backgroundColor: fill[3],
        borderColor: fill[3],
        data: contentDataQuality.map(c => (c.apbdes.score * 100).toFixed(2)),
        fill: false,
    });
    dataQualityGraph.update();
    createInfo();
    applyTableContent();
    onWidthChange(width);
}
function getStartSlice(widthCurrent, lengthLabel){
    var startSlice;
    if(widthCurrent <= 320)	
		startSlice = lengthLabel - 10;
	else if(widthCurrent > 320 && widthCurrent < 600)		
		startSlice = lengthLabel - 15;			
	else if(widthCurrent >=600 && widthCurrent <=900)	
		startSlice = lengthLabel - 35;					
	else
		startSlice = 0;
    return startSlice;
}
function getDataSlice(startSlice, originData){
    var tempData = $.extend(true, {}, originData);
    var endSlice = originData.labels.length;
    tempData.datasets=[];
    tempData.labels = originData.labels.slice(startSlice,endSlice)
	$.each(originData.datasets,function(idx,dataset){
		var temp = $.extend(true, {}, dataset)
		temp.data = temp.data.slice(startSlice,endSlice)
		tempData.datasets.push(temp)
	})
    return tempData
}

function onWidthChange(widthCurrent){	
    if($.isEmptyObject(cachedDataQualityGraph))cachedDataQualityGraph = $.extend(true,{},dataQualityGraph.data ) 
    var startSlice = getStartSlice(widthCurrent,cachedDataQualityGraph.labels.length)
    var data = getDataSlice(startSlice,cachedDataQualityGraph)
    dataQualityGraph.data.labels = data.labels;
    dataQualityGraph.data.datasets = data.datasets;
    dataQualityGraph.update()  
}

function applyTableHeader(header,thead){
	var tr = $('<tr>');
	$("tr",thead).remove()	
	$.each(header,function(idx,content){
		$('<th>').html(content).appendTo(tr);
	})		
	thead.append(tr);
}

function applyTableContent(){    
    var headerTableDaily = ["Tanggal","Berita","Penduduk","Anggaran","B.Qlt","B.Freq","P.Qlt","P.Qty","A.Qlt","A.Qty","Last Post", 
                        "#Post 1D", "#Post 1W","#Post 30D","Penduduk last Modified","#Penduduk", "Apbdes Last Modified","#Apbdes"]
    var headerTablePost = ["Score","Tanggal","Judul","#KBBI", "#Kalimat", "#Paragraph","%Gambar Utama","%Judul", "%KBBI","%Foto & Caption","%Kalimat","%Paragraph"]
    var tbody = $('#table-daily tbody');
    var thead = $('#table-daily thead');  
    
    applyTableHeader(headerTableDaily, thead)
    $.each(contentDataQuality,function(idx,content){
        var tr = $('<tr>');
        $('<td>').html(moment(content.date).format("DD MMM YYYY")).appendTo(tr);
        $('<td>').html(makeButtonScoring(content.blog.score)).appendTo(tr);
        $('<td>').html(makeButtonScoring(content.penduduk.score)).appendTo(tr)
        $('<td>').html(makeButtonScoring(content.apbdes.score)).appendTo(tr)
        $('<td>').html(content.blog.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.blog.score_frequency.toFixed(2)).appendTo(tr)
        $('<td>').html(content.penduduk.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.penduduk.score_quantity.toFixed(2)).appendTo(tr)
        $('<td>').html(content.apbdes.score_quality.toFixed(2)).appendTo(tr)
        $('<td>').html(content.apbdes.score_quantity.toFixed(2)).appendTo(tr)
        $('<td>').html(moment(content.blog.last_post).format("DD MMM YYYY")).appendTo(tr)
        $('<td>').html(content.blog.count_24h).appendTo(tr)
        $('<td>').html(content.blog.count_1w).appendTo(tr)
        $('<td>').html(content.blog.count_30d).appendTo(tr)
        $('<td>').html(moment(content.penduduk.last_modified).format("DD MMM YYYY")).appendTo(tr)
        $('<td>').html(content.penduduk.count).appendTo(tr)
        $('<td>').html(moment(content.apbdes.last_modified).format("DD MMM YYYY")).appendTo(tr)
        $('<td>').html(content.apbdes.count).appendTo(tr)
        tbody.append(tr);
    })

    var tbody = $('#table-post tbody');    
    var thead = $('#table-post thead');
    applyTableHeader(headerTablePost, thead)
    $.each(contentDataPost,function(idx,content){
        var tr = $('<tr>');
          $('<td>').html(makeButtonScoring(content.score)).appendTo(tr)
        $('<td>').html(moment(content.date).format("DD MMM YYYY")).appendTo(tr);
        $('<td>').html('<a href="'+content.url+'">'+content.title.substring(0,50)+'</a>').appendTo(tr)      
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

}
function createInfo(){
    if(info.desa!== null){
        $('#info-desa').text('Desa '+info.desa+', Kecamatan '+info.kecamatan+', Kabupaten '+info.kabupaten);
        $('#domain-url').attr("href","http://"+contentDataQuality[0].domain);
        $('#ckan-url').attr("href","http://data.prakarsadesa.id/organization/"+info.desa.toLowerCase().replace(/\s/g, ''));
    }
}

$(window).on('resize', function(){
	if($(this).width() != width){
		width = $(this).width();
		onWidthChange(width);		
	}
});

window.onload = function() {      
    applyGraph() 
};
