var columns = [
     {
	data: 'username',
	header: 'Username',
      },
      {
	data: 'id_supradesa',
	header: 'ID Supradesa',
      },
      {
	data: 'level',
	header: 'Level',
    type: 'dropdown',
    source: ['administrator','editor','author','contributor','subscriber'],
    width: 130,
      },
    ];
var container = document.getElementById('sheet');
var hot;                    
$.getJSON("/api/users_supradesa", function(data){
    if (data.length < 1) data ={};
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
    $.post( "/api/remove_users_supradesa", {data:JSON.stringify(hot.getSourceDataAtRow(selected[0]))}, function(){
		location.reload();
	});
});

$("#apply").click(function(){
	var data = hot.getSourceData();
    $.post( "/api/update_users_supradesa", {data:JSON.stringify(data)}, function(){
		location.reload();
	});
});