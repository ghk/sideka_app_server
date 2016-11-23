var columns = [
      {
	data: 'blog_id',
	header: 'ID',
	readOnly: true,
      },
      {
	data: 'kode',
	header: 'Kode',
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
      {	
	data: 'sekdes',
	header: 'Nama Sekdes',
      },
      {	
	data: 'kades',
	header: 'Nama Kades',
      },
    ];
$.getJSON("/api/desa", function(desas){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: desas,
	  columns: columns,
	  rowHeaders: true,
	  colHeaders: columns.map(c => c.header),
          afterChange: function(changes, source){
		if(source != "loadData"){
			changes.forEach(function(change){
				var allowedColumns = ["kode", "latitude", "longitude", "sekdes", "kades"];
				var column = change[1];	
				var value = change[3];
				var prevvalue = change[2];
				var id = hot.getDataAtCell(change[0], 0);
				if(id && allowedColumns.indexOf(column) >= 0 && prevvalue != value){
					$("#notification").html("Menyimpan...").show();
					$.post( "/api/desa", { blog_id: id, column: column, value: value})
					  .done(function( data ) {
						$("#notification").html("Penyimpanan Berhasil");
						setTimeout(function(){
							$("#notification").hide();
						}, 1000);
					  });
				}
			});
		}		
	  },
	});
	setTimeout(()=> hot.render(), 0);
});
