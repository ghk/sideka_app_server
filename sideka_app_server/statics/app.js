var columns = [
      {
	data: 'blog_id',
	header: 'ID',
	readOnly: true,
      },
      {
	data: 'kode',
	header: 'Kode',
	readOnly: true,
      },
      {
	data: 'domain',
	header: 'Domain',
	readOnly: true,
      },
      {	
	data: 'desa',
	header: 'Desa',
      },
      {
	data: 'latitude',
	header: 'Latitude',
	format: '0.0000000',
	type: 'numeric',
      },
      {
	data: 'longitude',
	header: 'Longitude',
	format: '0.0000000',
	type: 'numeric',
      },
      {	
	data: 'kecamatan',
	header: 'Kecamatan',
	readOnly: true,
      },
      {	
	data: 'kabupaten',
	header: 'Kabupaten',
	readOnly: true,
      },
      {	
	data: 'propinsi',
	header: 'Propinsi',
	readOnly: true,
      },
    ];
$.getJSON("/api/desa", function(desas){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: desas,
	  minSpareCols: 1,
	  minSpareRows: 1,
	  columns: columns,
	  rowHeaders: true,
	  colHeaders: columns.map(c => c.header),
	});
});
