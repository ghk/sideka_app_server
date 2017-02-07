var columns = [
     {
	data: 'username',
	header: 'Username',
      },
      {
	data: 'region_prefix',
	header: 'Kode Region',
      },
    ];
var container = document.getElementById('sheet');
var hot;                    
$.getJSON("/api/users_supradesa", function(data){
    hot = new Handsontable(container, {
        data: data,
        columns: columns,
        rowHeaders: true,
        colHeaders: columns.map(c => c.header),
        outsideClickDeselects: false,
    });
    setTimeout(()=> hot.render(), 0);
});

$( "#insertRow" ).click(function() {
    hot.alter("insert_row", 10);
    hot.selectCell(0, 0, 0, 0, true);
    hot.render();
});

$("#removeRow").click(function(){
	var selected = hot.getSelected();
    $.post( "/api/remove_users_supradesa", {data:JSON.stringify(hot.getDataAtRow(selected[0]))}, function(){
		location.reload();
	});
});

$("#apply").click(function(){
	var data = hot.getSourceData();
    $.post( "/api/update_users_supradesa", {data:JSON.stringify(data)}, function(){
		location.reload();
	});
});