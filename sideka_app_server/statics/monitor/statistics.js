var header = ['Wp Id','Domain','Berita', 'Penduduk','Anggaran','B. Qlt','B. Freq','P. Qlt', 'P. Qty', 
'A. Qlt','A. Qty','Last Post','#Post 1D', '#Post 1W', '#Post 30D','Penduduk Last Modified', '# Penduduk', 'APBDes Last Modified','# APBDes',]
var applyHeaderandFooter =function(){
	$('#table-data-quality thead > tr').remove()
	var thead = $('#table-data-quality thead');
	var tr = $('<tr>');
	for(var i = 0;i < header.length;i++){
		$('<th>').html(header[i]).appendTo(tr);		
	}
	thead.append(tr);
}

var makeButtonScoring = function(score){
	var classButton;
	score *=100;	
	if(score < 40)
		classButton= 'uk-badge uk-badge-danger';
	else if(score < 70) 
		classButton ='uk-badge uk-badge-warning'; 
	else
		classButton ='uk-badge uk-badge-success';	
	return '<span class="'+classButton+'">'+score.toFixed(2)+'</span>';;
}

var changeSelected = function(supradesa_id){	
	$('#table-data-quality thead > tr').remove()
	$('#table-data-quality tbody > tr').remove()

	applyHeaderandFooter();
	$.getJSON("/api/statistics?supradesa_id="+supradesa_id, function(data){
		var tbody = $('#table-data-quality tbody');
		var origin = window.location.origin;
		var pathName = window.location.pathname;	
		var url = origin +"/statistic/";
		$.each(data,function(idx,content){
			var tr = $('<tr>');
			$('<td>').html('<a href="'+ url +content.blog_id+'">'+content.blog_id+'</a>').appendTo(tr);
			$('<td>').html('<a href="http://'+content.domain+'">'+content.domain+'</a>').appendTo(tr);
			$('<td class="uk-text-center">').html(makeButtonScoring(content.blog.score)).appendTo(tr);
			$('<td class="uk-text-center">').html(makeButtonScoring(content.penduduk.score)).appendTo(tr);
			$('<td class="uk-text-center">').html(makeButtonScoring(content.apbdes.score)).appendTo(tr);
			$('<td>').html((content.blog.score_quality *100).toFixed(2)).appendTo(tr);
			$('<td>').html((content.blog.score_frequency *100).toFixed(2)).appendTo(tr);
			$('<td>').html((content.penduduk.score_quality *100).toFixed(2)).appendTo(tr);
			$('<td>').html((content.penduduk.score_quantity *100).toFixed(2)).appendTo(tr);
			$('<td>').html((content.apbdes.score_quality *100).toFixed(2)).appendTo(tr);
			$('<td>').html((content.apbdes.score_quantity *100).toFixed(2)).appendTo(tr);
			$('<td>').html(content.blog.last_post).appendTo(tr);
			$('<td>').html(content.blog.count_24h).appendTo(tr);
			$('<td>').html(content.blog.count_1w).appendTo(tr);
			$('<td>').html(content.blog.count_30d).appendTo(tr);
			$('<td>').html(content.penduduk.last_modified).appendTo(tr);
			$('<td>').html(content.penduduk.count).appendTo(tr);			
			$('<td>').html(content.apbdes.last_modified).appendTo(tr);	
			$('<td>').html(content.apbdes.count).appendTo(tr);		
			tbody.append(tr);
			
		})
	})
}
changeSelected(hashUrl());
$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
	changeUrl(value) 
});


