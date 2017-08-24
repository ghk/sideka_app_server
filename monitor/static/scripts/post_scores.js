var currentPage = 1;itemPerPage = 50; totalItems = 0; dataTables = [];
var headers = ['Domain', 'Score', 'Title','#KBBi','#Kalimat','#Paragraph', '% Gambar Utama','% Title', '% Foto&Caption', '% KBBI', '% Kalimat', '% Paragraph', 'Tanggal']

function applyHeader(){
	var thead = $("#table-post-scores > thead");
	var tr = $('<tr>')
	$("tr",thead).remove();
	$.each(headers,function(idx,item){
		$('<th>').html(item).appendTo(tr);
	})
	thead.append(tr);
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

function pagination(page){
	$("#pagination >ul").remove()
	$("#pagination").pagination({
        items: page,
        itemsOnPage: itemPerPage,
        cssStyle: 'light-theme',
		hrefTextSuffix:"",
		onPageClick:function(pageNumber,event){
			onSupradesaChanged(pageNumber,hashUrl());
		}
    });
}

function applyContent(data){	
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

function getCountPost(supradesaId){
	$.getJSON("/api/count_post_scores?supradesa_id="+supradesaId, function(data){
		pagination(data)
	});
}

function onSupradesaChanged(pageBegin, supradesaId){	
	$.getJSON("/api/post_scores?pagebegin="+pageBegin+"&itemperpage="+itemPerPage+"&supradesa_id="+supradesaId, function(data){
		applyContent(data)
	}); 		
	changeUrl(supradesaId);
}

$('#select-supradesa').change(function(){
	var supradesaId = $(this).val();
	getCountPost(supradesaId);
	onSupradesaChanged(1,supradesaId);
});

window.onload = function(){
	var supradesaId = hashUrl()
	applyHeader();	
	getCountPost(supradesaId);
	onSupradesaChanged(1,supradesaId)
}

