contentDataQuality = contentDataQuality.filter(function(c){c.date !=="None"}) 
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000"];
var width = $(window).width();
var cachedDataQualityGraph={},cachedDataActivityGraph={};
var configDataQualityGraph= {
	type: 'line',
	data: {
		labels: [],
		datasets: [{
            label: "Berita",
            backgroundColor: fill[1],
            borderColor: fill[1],
            data:[],
            fill: false,
        }, {
            label: "Penduduk",       
            backgroundColor: fill[2],
            borderColor: fill[2],
            data:[],
            fill: false,
        },{
            label: "Anggaran",
            backgroundColor: fill[3],
            borderColor: fill[3],
            data:[],
            fill: false,
        }],
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
var dataQualityGraph = new Chart(getContext(canvasDataQuality), configDataQualityGraph);

var configActivityGraph = $.extend(true,{},configDataQualityGraph);
configActivityGraph.options.scales.yAxes[0].scaleLabel.labelString = "#Aktifitas"
var canvasDataActivity = document.getElementById('data-activity-graph');
var dataActivityGraph = new Chart(getContext(canvasDataActivity), configActivityGraph);
    
function getContext (canvas){
	if (canvas.getContext){
		var ctx = canvas.getContext('2d');
		ctx.fillStyle = 'black';
		ctx.font = '26px Arial';
		ctx.fillText('0', 0, 26);
		return ctx
	}
}

function applyDatasets(graph,datasets,custom){
    $.each(graph.data.datasets,function(idx,dataset){
        if(!$.isEmptyObject(custom))
            dataset[custom.property] = custom.content[idx];  
        dataset.data = datasets[idx]
    })
}

function applyGraph(){
    var datasets=[contentDataQuality.map(function(c){(c.blog.score * 100).toFixed(2)}),contentDataQuality.map(function(c){(c.penduduk.score * 100).toFixed(2)}),contentDataQuality.map(function(c){(c.apbdes.score * 100).toFixed(2)}),]
    applyDatasets(dataQualityGraph,datasets)
    dataQualityGraph.data.labels = contentDataQuality.map(function(content, idx){return (idx%7 ==0)?moment(content.date).format("DD MMM YYYY"):"";}) 
    dataQualityGraph.update();

    var custom = {property:"label",content:["Berita Harian","Kependudukan","Keuangan"]}
    datasets = [contentDataActivity.post,contentDataActivity.penduduk,contentDataActivity.apbdes]
    applyDatasets(dataActivityGraph,datasets,custom)
    dataActivityGraph.data.labels = contentDataActivity.label.map(function(timestamp, idx){return (idx%7 ==0 ||idx == contentDataActivity.label.length-1)?moment.unix(timestamp).format("DD MMM YYYY"):"";})    
    dataActivityGraph.update();

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

function sliceDataGraph(graph,startSlice, data){
    var result = {labels:[],datasets:[]}
    var endSlice = data.labels.length;
    result.labels = data.labels.slice(startSlice,endSlice)
	$.each(data.datasets,function(idx,dataset){
		var temp = $.extend(true, {}, dataset)
		temp.data = temp.data.slice(startSlice,endSlice)
		result.datasets.push(temp)
	})
    graph.data.labels = result.labels;
    graph.data.datasets = result.datasets;
}

function onWidthChange(widthCurrent){	
    if($.isEmptyObject(cachedDataQualityGraph))cachedDataQualityGraph = $.extend(true,{},dataQualityGraph.data ) 
    var startSlice = getStartSlice(widthCurrent,cachedDataQualityGraph.labels.length)
    sliceDataGraph(dataQualityGraph,startSlice,cachedDataQualityGraph)    
    dataQualityGraph.update()  
    
    if($.isEmptyObject(cachedDataActivityGraph))cachedDataActivityGraph = $.extend(true,{},dataActivityGraph.data ) 
    var startSlice = getStartSlice(widthCurrent,cachedDataActivityGraph.labels.length)
    sliceDataGraph(dataActivityGraph,startSlice,cachedDataActivityGraph)
    dataActivityGraph.update()  
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
        $('#ckan-url').removeClass("hidden").attr("href","http://data.prakarsadesa.id/organization/"+info.desa.toLowerCase().replace(/\s/g, ''));           
    }
    $('#domain-url').removeClass("hidden").attr("href","http://"+info.domain);    
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
