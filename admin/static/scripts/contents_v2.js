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

var getUrl = function(){
	var params = {};
	var filter=$("input[name='desa-filter']").val();
	if(filter){
		if(parseInt(filter))
			params["desa_id"] =filter;
		else
			params["domain"] = filter;
	}
	var type_filter=$("[name='type']").val();
	if(type_filter){
		params["type"]=type_filter;
	}
	return "/api/contents/v2?"+$.param(params);
}

$.getJSON(getUrl(), function(data){
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


var filter = function(){
	$.getJSON(getUrl(), function(data){
		hot.loadData(data);
		setTimeout(()=> hot.render(), 0);
	});
};
$("#filter-form").submit(function(){
	filter();
	return false;
});

$("#filter-form select").change(function(){
	filter();
});
