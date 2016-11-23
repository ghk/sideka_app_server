schema.forEach(c => {
	c.readOnly = true;
});
var container = document.getElementById('sheet');

var hot = new Handsontable(container, {
  data: content.data,
  columns: schema,
  rowHeaders: true,
  colHeaders: schema.map(c => c.header),
});
setTimeout(()=> hot.render(), 0);
