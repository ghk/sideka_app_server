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
	renderer: makeLinkRenderer(v => "https://sideka.id/wp-admin/network/site-info.php?id="+v, v => v),
	readOnly: true,
      },
      {
	data: 'kode',
	header: 'Kode',
      },
      {
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(v => "http://"+v, v => v),
	readOnly: true,
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
	data: 'desa',
	header: 'Desa',
	readOnly: true,
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
      {	
	data: 'pendamping',
	header: 'Pendamping',
      },
    ];
$.getJSON("/api/desa", function(desas){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: desas,
	  columns: columns,
	  columnSorting: true,
	  sortIndicator: true,
	  rowHeaders: true,
	  colHeaders: columns.map(c => c.header),
          afterChange: function(changes, source){
		if(source != "loadData"){
			changes.forEach(function(change){
				var allowedColumns = ["kode", "latitude", "longitude", "sekdes", "kades", "pendamping"];
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

$("#btn-update-from-code").click(function(){
	console.log("updating");
	$.post("/api/update_desa_from_code", function(){
		location.reload();
	});
});

$("#btn-update-sd-desa").click(function(){
	console.log("updating");
	$.post("/api/update_sd_desa", function(){
		location.reload();
	});
});
