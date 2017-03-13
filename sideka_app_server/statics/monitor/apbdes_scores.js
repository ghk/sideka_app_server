var header = ['Domain','Tahun','Pendapatan', 'Belanja', '# Baris','Last Modified' ];

function getSubtype(data){
	var unique=[];
	data.map(function(c){
		if(unique.indexOf(c.subtype)==-1 && c.subtype != "null")unique.push(c.subtype);		
	});
	return unique.sort();
}

function currencyConvert(n, currency) {
    return currency + "\t " + n.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
}

function applyContent(data,subtypes){
	$("#years-apbdes >li").remove();
	$("#content-apbdes >li").remove();

	$.each(subtypes,function(idx, subtype){
		var tableContent = $("#table-content").clone().removeClass("hidden");
		var tbody = $("tbody", tableContent);
		var dataFiltered = data.filter(function(c){c.subtype == subtype})		
		var li = $('<li>');

		$('<a>').attr("href","").append(subtype).appendTo(li)
		if (idx==0)li.addClass("uk-active");
		$("#years-apbdes").append(li);			
		$.each(dataFiltered,function(i, content){
			var tr = $('<tr>');
			$('<td>').html('<a href="http://'+content.domain+'">'+content.domain+'</a>').appendTo(tr);
			$('<td>').html(currencyConvert(content.pendapatan, "Rp")).appendTo(tr);
			$('<td>').html(currencyConvert(content.belanja,"Rp")).appendTo(tr);
			$('<td>').html(content.rows).appendTo(tr);
			$('<td>').html(content.last_modified).appendTo(tr);
			tbody.append(tr);
		})	 
		li = $('<li>').append(tableContent);
		if(idx==0)li.addClass("uk-active");
		$("#content-apbdes").append(li);
	})	
}

function onSupradesaChanged(supradesaId){
	$.getJSON("/api/apbdes_scores?supradesa_id="+supradesaId, function(data){
		var subtype = getSubtype(data)
		applyContent(data,subtype)
	});
	changeUrl(supradesaId)
}

$('#select-supradesa').change(function(){
	var supradesaId = $(this).val();
	onSupradesaChanged(supradesaId);	
});

window.onload = function(){
	onSupradesaChanged(hashUrl());
}
