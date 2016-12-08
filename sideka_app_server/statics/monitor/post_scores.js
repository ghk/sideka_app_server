function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}
function postRenderer(instance, td, row, col, prop, value, cellProperties) {
	var r = instance.getDataAtRow(row);
	td.innerHTML = "<a href='"+r[10]+"'>"+value+"</a>";
	return td;
}
var columns = [
      {
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(v => "http://"+v, v => v),
      },
      {	
	data: 'score',
	header: 'Score',
	type: 'numeric',
	format: '0.00',
      },
      {	
	data: 'title',
	header: 'Title',
	renderer: postRenderer,
      },
      {	
	data: 'has_thumbnail',
	header: 'Image?',
      },
      {	
	data: 'words',
	header: '# Words',
      },
      {	
	data: 'kbbi',
	header: '# KBBI Words',
      },
      {	
	data: 'kbbi_percentage',
	header: '% KBBI',
      },
      {
	data: 'sentences',
	header: '# Sentences',
      },
      {
	data: 'paragraphs',
	header: '# Paragraphs',
      },
      {
	data: 'date',
	header: 'Date',
      },
      {
	data: 'url',
	header: 'URL',
	renderer: function(a, td){return td;},
      },
    ];
columns.forEach(c => {
	c.readOnly = true;
});
$.getJSON("/api/post_scores", function(data){
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
