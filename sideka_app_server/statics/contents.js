var columns = [
      {
	data: 'id',
	header: 'ID',
      },
      {
	data: 'desa_id',
	header: 'ID Desa',
      },
      {
	data: 'desa',
	header: 'Desa',
      },
      {	
	data: 'type',
	header: 'Type',
      },
      {
	data: 'subtype',
	header: 'SubType',
      },
      {
	data: 'timestamp',
	header: 'Timestamp',
      },
      {	
	data: 'date_created',
	header: 'Date Created',
	readOnly: true,
      },
      {	
	data: 'user_login',
	header: 'Created By',
      },
      {	
	data: 'opendata_date_pushed',
	header: 'Date Pushed',
      },
      {	
	data: 'opendata_push_error',
	header: 'Push Error',
      },
    ];
columns.forEach(c => {
	c.readOnly = true;
});
$.getJSON("/api/contents", function(data){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: data,
	  columns: columns,
	  rowHeaders: true,
	  colHeaders: columns.map(c => c.header),
	});
	setTimeout(()=> hot.render(), 0);
});
