contentDataQuality = contentDataQuality.filter(function(c){return c.date !=="None"}) 
var fill = ["#8bc34a", "#d84315", "#2196f3", "#ffa000", "#9467bd"];
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
        },{
            label: "Pemetaan",
            backgroundColor: fill[4],
            borderColor: fill[4],
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
    var datasets=[
		contentDataQuality.map(function(c){return (c.blog.score * 100).toFixed(2)}),	
		contentDataQuality.map(function(c){return (c.penduduk ? c.penduduk.score * 100 : 0).toFixed(2)}),
		contentDataQuality.map(function(c){return (c.keuangan ? c.keuangan.score * 100 : 0).toFixed(2)}),
		contentDataQuality.map(function(c){return (c.pemetaan ? c.pemetaan.score * 100 : 0).toFixed(2)})
	];
    applyDatasets(dataQualityGraph,datasets)
    dataQualityGraph.data.labels = contentDataActivity.label.map(function(timestamp, idx){return (idx%7 ==0 ||idx == contentDataActivity.label.length-1)?moment.unix(timestamp).format("DD MMM YYYY"):"";})    
    dataQualityGraph.update();

    var custom = {property:"label",content:["Berita Harian","Kependudukan","Keuangan", "Pemetaan"]}
    datasets = [contentDataActivity.post,contentDataActivity.penduduk,contentDataActivity.keuangan, contentDataActivity.pemetaan]
    applyDatasets(dataActivityGraph,datasets,custom)
    dataActivityGraph.data.labels = contentDataActivity.label.map(function(timestamp, idx){return (idx%7 ==0 ||idx == contentDataActivity.label.length-1)?moment.unix(timestamp).format("DD MMM YYYY"):"";})    
    dataActivityGraph.update();

    createInfo();
    applyTableContent();
    var width = $(window).width();
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
    return [startSlice, lengthLabel];
}

function sliceDataGraph(graph,startSlice, sliceLength, data){
    var result = {labels:[],datasets:[]}
    result.labels = data.labels.slice(startSlice,startSlice+sliceLength)
	$.each(data.datasets,function(idx,dataset){
		var temp = $.extend(true, {}, dataset)
		temp.data = temp.data.slice(startSlice,startSlice+sliceLength)
		result.datasets.push(temp)
	})
    graph.data.labels = result.labels;
    graph.data.datasets = result.datasets;
}

function onWidthChange(widthCurrent){	
    if($.isEmptyObject(cachedDataQualityGraph))cachedDataQualityGraph = $.extend(true,{},dataQualityGraph.data ) 
    var sliceConfig = getStartSlice(widthCurrent,cachedDataQualityGraph.labels.length)
    var startSlice = sliceConfig[0], sliceLength = sliceConfig[1];
    sliceDataGraph(dataQualityGraph,startSlice, sliceLength,cachedDataQualityGraph)    
    dataQualityGraph.update()  
    
    if($.isEmptyObject(cachedDataActivityGraph))cachedDataActivityGraph = $.extend(true,{},dataActivityGraph.data ) 
    startSlice = cachedDataActivityGraph.labels.length - sliceLength;
    sliceDataGraph(dataActivityGraph,startSlice, sliceLength,cachedDataActivityGraph)
    dataActivityGraph.update()  
}

function score(content, props, content_id_props){
 	var classButton;
 	var buttonResult;
	var s = content;
	props = props.split(".");
	for(var i = 0; i <props.length; i++){
		if(!s){
			return "-";
		}
		s = s[props[i]];
	}
	if(!s || !s.toFixed){
		return "-";
	}
 	s *=100;
	link = null;
	if(content_id_props){
		content_id_props = content_id_props.split(".");
		id = content;
		for(var i = 0; i <content_id_props.length; i++){
			if(!id){
				break;
			}
			id = id[content_id_props[i]];
		}
		if(id){
			link = "http://admin.sideka.id/contents/v2/"+id+"/data";
		}
	}
 	
 	if(s < 40)
 		classButton= 'uk-badge uk-badge-danger';
 	else if(s < 70) 
 		classButton ='uk-badge uk-badge-warning'; 
 	else
 		classButton ='uk-badge uk-badge-success';
	if(!link){
		link = "#";
	}
 	buttonResult = '<a href="'+link+'" class="'+classButton+'">'+s.toFixed(2)+'</a>';
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
    var headerTableDaily = ["Tanggal","Berita","Penduduk","Anggaran", "Pemetaan", "B.Qlt","B.Freq","P.Pen","P.Sur","P.Mut","K.Ren","K.Ang", 
                        "K.SPP", "K.TBP","Pt. Tra","Pt. Bou","Pt. Wat", "Pt. Fac","Pt. Lan"]
    var headerTablePost = ["Score","Tanggal","Judul","#KBBI", "#Kalimat", "#Paragraph","%Gambar Utama","%Judul", "%KBBI","%Foto & Caption","%Kalimat","%Paragraph"]
    var tbody = $('#table-daily tbody');
    var thead = $('#table-daily thead');  
    
    applyTableHeader(headerTableDaily, thead)
    $.each(contentDataQuality.slice(0).reverse(), function(idx,content){
        var tr = $('<tr>');
        $('<td>').html(moment(content.date * 1000).format("DD MMM YYYY")).appendTo(tr);
        $('<td>').html(score(content, "blog.score")).appendTo(tr);
        $('<td>').html(score(content, "penduduk.score", "penduduk.content_id")).appendTo(tr);
        $('<td>').html(score(content, "keuangan.score")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.score", "pemetaan.content_id")).appendTo(tr);
        $('<td>').html(score(content, "blog.score_quality")).appendTo(tr);
        $('<td>').html(score(content, "blog.score_frequency")).appendTo(tr);
        $('<td>').html(score(content, "penduduk.penduduk.score")).appendTo(tr);
        $('<td>').html(score(content, "penduduk.log_surat.score")).appendTo(tr);
        $('<td>').html(score(content, "penduduk.mutasi.score")).appendTo(tr);
        $('<td>').html(score(content, "keuangan.perencanaan.score", "keuangan.perencanaan.content_id")).appendTo(tr);
        $('<td>').html(score(content, "keuangan.pengaggaran.score", "keuangan.penganggaran.content_id")).appendTo(tr);
        $('<td>').html(score(content, "keuangan.spp.score", "keuangan.spp.content_id")).appendTo(tr);
        $('<td>').html(score(content, "keuangan.penerimaan.score", "keuangan.penerimaan.content_id")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.network_transportation.score")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.boundary.score")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.waters.score")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.facilities_infrastructures.score")).appendTo(tr);
        $('<td>').html(score(content, "pemetaan.landuse.score")).appendTo(tr);
        tbody.append(tr);
    })

    var tbody = $('#table-post tbody');    
    var thead = $('#table-post thead');
    applyTableHeader(headerTablePost, thead)
    $.each(contentDataPost,function(idx,content){
        var tr = $('<tr>');
          $('<td>').html(score(content, "score")).appendTo(tr)
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
        $('#info-desa').text(info.desa+', '+info.kecamatan+', '+info.kabupaten);
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
