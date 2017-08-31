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
        data: 'd0',
        header: 'Data 0',
      },
      {
        data: 'd1',
        header: 'Data 1',
      },
      {
        data: 'd2',
        header: 'Data 2',
      },
      {
        data: 'd3',
        header: 'Data 3',
      },
      {
        data: 'added',
        header: 'Added',
      },
      {
        data: 'modified',
        header: 'Modified',
      },
      {
        data: 'deleted',
        header: 'Deleted',
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

var hot;

$.getJSON("/api/contents/v2", function(data){
	var container = document.getElementById('sheet');

	hot = new Handsontable(container, {
	  data: data,
	  columns: columns,
	  rowHeaders: true,
    renderAllRows: false,
	  colHeaders: columns.map(c => c.header),
	});
	setTimeout(()=> hot.render(), 0);
});

$("#filter-form").submit(function(){
	var desa_id=$("input[name='filter-textbox']").val();
	var query_string = "";
	if(desa_id)
		query_string = "?desa_id="+desa_id;
	$.getJSON("/api/contents/v2"+query_string, function(data){
		hot.loadData(data);
		setTimeout(()=> hot.render(), 0);
	});
	return false;
});
