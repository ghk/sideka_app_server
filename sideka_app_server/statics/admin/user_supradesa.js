var columns = [
      {
	data: 'username',
	header: 'Username',
      },
      {
	data: 'code',
	header: 'Kode Region',
      },
    ];
var container = document.getElementById('sheet');
var hot = new Handsontable(container, {
    data: {},
    columns: columns,
    rowHeaders: true,
    colHeaders: columns.map(c => c.header),
});
setTimeout(()=> hot.render(), 0);

$( "#insertRow" ).click(function() {
    hot.alter("insert_row", 0);
    hot.selectCell(0, 0, 0, 0, true);
    hot.render();
});