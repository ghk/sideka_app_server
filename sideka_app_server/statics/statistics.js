function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}
var columns = [
      {
	data: 'blog_id',
	header: 'Wordpress ID',
      },
      {
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(v => "http://"+v, v => v),
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
