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
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(v => "http://"+v, v => v),
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
columns.forEach(c => {
	c.readOnly = true;
});
$.getJSON("/api/statistics", function(data){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: data,
	  columns: columns,
          columnSorting: true,
          sortIndicator: true,
	  rowHeaders: true,
	  colHeaders: columns.map(c => c.header),
	});
	setTimeout(()=> hot.render(), 0);
});
