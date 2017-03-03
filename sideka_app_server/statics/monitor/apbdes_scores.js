var header = ['Domain','Tahun','Pendapatan', 'Belanja', '# Baris','Last Modified' ];

var getSubtype=function(data){
	var unique=[];
	data.map(function(c){
		if(unique.indexOf(c.subtype)==-1 && c.subtype != "null")unique.push(c.subtype);		
	});
	return unique.sort();
}
var currencyConvert = function (n, currency) {
    return currency + "\t " + n.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
}

var applyContent = function(data,subtypes){
	$("#years-apbdes >li").remove();
	$("#content-apbdes >li").remove();

	$.each(subtypes,function(idx, subtype){
		var tableContent = $("#table-content").clone().removeClass("hidden");
		var tbody = $("tbody", tableContent);
		var dataFiltered = data.filter(c=>c.subtype == subtype)		
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

var changeSelected = function(supradesa_id){
	$.getJSON("/api/apbdes_scores?supradesa_id="+supradesa_id, function(data){
		var subtype = getSubtype(data)
		applyContent(data,subtype)
	});
}


changeSelected(hashUrl());
$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
	changeUrl(value)
});
