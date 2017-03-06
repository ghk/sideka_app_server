var currentPage = 1;itemPerPage = 50; totalItems = 0; dataTables = [];
var headers = ['Domain', 'Score', 'Title','#KBBi','#Kalimat','#Paragraph', '% Gambar Utama','% Title', '% Foto&Caption', '% KBBI', '% Kalimat', '% Paragraph', 'Tanggal']

var applyHeader = function(){
	var thead = $("#table-post-scores > thead");
	var tr = $('<tr>')
	$("tr",thead).remove();
	$.each(headers,function(idx,item){
		$('<th>').html(item).appendTo(tr);
	})
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
var pagination = function(page){
	$("#pagination >ul").remove()
	$("#pagination").pagination({
        items: page,
        itemsOnPage: itemPerPage,
        cssStyle: 'light-theme',
		hrefTextSuffix:"",
		onPageClick:function(pageNumber,event){
			getPost(pageNumber,hashUrl());
		}
    });
}

var applyContent = function(data){	
	var tbody = $("#table-post-scores > tbody");
	var tr = $('<tr>')

	$("tr",tbody).remove()	
	$.each(data,function(i,content){
		tr = $('<tr>');		
		$('<td>').append($('<a>').attr("href", content.url).text(content.domain)).appendTo(tr);
		$('<td>').html(makeButtonScoring(content.score)).appendTo(tr);
		$('<td>').append($('<a>').attr("href", content.url).text(content.title.substring(0,50))).appendTo(tr)
		$('<td>').html(content.kbbi).appendTo(tr);
		$('<td>').html(content.sentences).appendTo(tr);
		$('<td>').html(content.paragraphs).appendTo(tr);
		$('<td>').html((content.has_thumbnail*10).toFixed(2)).appendTo(tr);						
		$('<td>').html((content.score_title*10).toFixed(2)).appendTo(tr);	
		$('<td>').html((content.score_caption*15).toFixed(2)).appendTo(tr);	
		$('<td>').html((content.kbbi_percentage*20).toFixed(2)).appendTo(tr);	
		$('<td>').html((content.score_sentences*15).toFixed(2)).appendTo(tr);	
		$('<td>').html((content.score_paragraphs*20).toFixed(2)).appendTo(tr);	 
		$('<td>').html(content.date).appendTo(tr);	
		tbody.append(tr);	
	})
}
var getCountPost = function(supradesa_id){
	$.getJSON("/api/count_post_scores?supradesa_id="+supradesa_id, function(data){
		pagination(data)
	});
}
var getPost = function(pageBegin, supradesa_id){
	$.getJSON("/api/post_scores?pagebegin="+pageBegin+"&itemperpage="+itemPerPage+"&supradesa_id="+supradesa_id, function(data){
		applyContent(data)
	}); 	
}

$('#select-supradesa').change(function(){
	var value = $(this).val();
	getCountPost(value);
	getPost(1,value);
	changeUrl(value);
});

var supradesa_id = hashUrl()
applyHeader();
getCountPost(supradesa_id);
getPost(1,supradesa_id)

