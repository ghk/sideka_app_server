var header = ['Domain','Tahun','Pendapatan', 'Belanja', '# Baris','Last Modified' ];

var getSubtype=function(data){
	var unique=[];
	data.map(function(c){
		if(unique.indexOf(c.subtype)==-1 && c.subtype != "null")unique.push(c.subtype);		
	});
	return unique.sort();
}
var currencyConvert = function (n, currency) {
    return currency + " " + n.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
}

var applyContent = function(data,subtype){
	$("#years-apbdes >li").remove();
	$("#content-apbdes >li").remove();

	for(var i=0;i < subtype.length;i++){
		var tableContent = $("#table-content").clone().removeClass("hidden");
		var tbody = $("tbody", tableContent);
		var dataFiltered = data.filter(c=>c.subtype == subtype[i])		
		var li = $('<li>');

		$('<a>').attr("href","").append(subtype[i]).appendTo(li)
		if (i ==0)li.addClass("uk-active");
		$("#years-apbdes").append(li);			
		$.each(dataFiltered,function(idx, row){
			var tr = $('<tr>');
			$('<td>').html('<a href="http://'+row.domain+'">'+row.domain+'</a>').appendTo(tr);
			$('<td>').html(currencyConvert(row.pendapatan, "Rp")).appendTo(tr);
			$('<td>').html(currencyConvert(row.belanja,"Rp")).appendTo(tr);
			$('<td>').html(row.rows).appendTo(tr);
			$('<td>').html(row.last_modified).appendTo(tr);
			tbody.append(tr);
		})	 
		li = $('<li>').append(tableContent);
		if(i==0)li.addClass("uk-active");
		$("#content-apbdes").append(li);
	}	
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
