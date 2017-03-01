/*
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
	data: 'blog_id',
	header: 'Wordpress Id',
	renderer: makeLinkRenderer(function(v){ return  "/statistic/"+v }, function(v) {return v; }),
		},
		{
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(function(v){ return  "http://"+v }, function(v) {return v; }),
      },

      {
	data: 'pendamping',
	header: 'Pendamping',
      },

      {
	data: 'blog.score',
	header: 'Berita',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'penduduk.score',
	header: 'Penduduk',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'apbdes.score',
	header: 'Anggaran',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'blog.score_quality',
	header: 'B. Qlt',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'blog.score_frequency',
	header: 'B. Freq',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'penduduk.score_quality',
	header: 'P. Qlt',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'penduduk.score_quantity',
	header: 'P. Qty',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'apbdes.score_quality',
	header: 'A. Qlt',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'apbdes.score_quantity',
	header: 'A. Qty',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'blog.last_post',
	header: 'Last Post',
      },
      {
	data: 'blog.count_24h',
	header: '#Post 1D',
      },
      {
	data: 'blog.count_1w',
	header: '#Post 1W',
      },
      {
	data: 'blog.count_30d',
	header: '#Post 30D',
      },
      {
	data: 'penduduk.last_modified',
	header: 'Penduduk Last Modified',
      },
      {
	data: 'penduduk.count',
	header: '# Penduduk',
      },
      {
	data: 'apbdes.last_modified',
	header: 'APBDes Last Modified',
      },
      {
	data: 'apbdes.count',
	header: '# APBDes',
      },
    ];
columns.forEach(function(c) {
	c.readOnly = true;
});
var changeSelected = function(supradesa_id){
	$.getJSON("/api/statistics?supradesa_id="+supradesa_id, function(data){
		var container = document.getElementById('sheet');

		var hot = new Handsontable(container, {
		data: data,
		columns: columns,
		columnSorting: true,
		sortIndicator: true,
		rowHeaders: true,
		colHeaders: columns.map(function(c) { return c.header; }),
		});
		setTimeout(function(){ hot.render() }, 0);
	});	
}

changeSelected(hashUrl());
$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
	changeUrl(value) 
});
*/


var convertDate = function(date){
  var value = new Date(date)
  var monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  return value.getDate() + " " + monthNames[value.getMonth()] + " " + value.getFullYear();
}

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


