function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}
var columns = [
      {
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(function(v) { return "http://"+v}, function(v) { return v; }),
      },
      {	
	data: 'subtype',
	header: 'Tahun',
      },
      {	data: 'pendapatan',
	header: 'Pendapatan',
	type: 'numeric',
	format: '0,0',
      },
      {	
	data: 'belanja',
	header: 'Belanja',
	type: 'numeric',
	format: '0,0',
      },
      {	
	data: 'rows',
	header: '# Baris',
      },
      {
	data: 'last_modified',
	header: 'Last Modified',
      },
    ];
columns.forEach(function(c) {
	c.readOnly = true;
});
var changeSelected = function(){
	var supradesa_id = $( "#select-supradesa option:selected" ).val();

	$.getJSON("/api/apbdes_scores?supradesa_id="+supradesa_id, function(data){
		var container = document.getElementById('sheet');

		var hot = new Handsontable(container, {
		data: data.filter(function(d) { return d.pendapatan && d.belanja; }),
		columns: columns,
		columnSorting: true,
		sortIndicator: true,
		rowHeaders: true,
		colHeaders: columns.map(function(c) {return c.header;}),
		});
		setTimeout(function(){ hot.render()}, 0);
	});
}
changeSelected();
$('#select-supradesa').change(function(){
	var value = $(this).val();
	changeSelected(value)
});
