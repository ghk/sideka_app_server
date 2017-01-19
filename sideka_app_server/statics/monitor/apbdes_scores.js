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
$.getJSON("/api/apbdes_scores", function(data){
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
