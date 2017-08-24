function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}

var columns = [
      {
        data: 'id',
        header: 'ID',
        renderer: makeLinkRenderer(v => "/contents/v2/"+v+"/data?sheet=null", v => v),
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
       {	
        data: 'change_id',
        header: 'Change Id',
      },
    ];
columns.forEach(c => {
	c.readOnly = true;
});

$.getJSON("/api/contents/v2", function(data){
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
	  data: data,
	  columns: columns,
	  rowHeaders: true,
    renderAllRows: false,
	  colHeaders: columns.map(c => c.header),
	});
	setTimeout(()=> hot.render(), 0);
});
