var columns = [
     {
	data: 'id',
	header: 'ID',
      readOnly:true,
      },
      {
	data: 'region_code',
	header: 'Kode Region',
      },
      {
	data: 'flag',
	header: 'flag',
      },
      {
	data: 'name',
	header: 'Nama',
      },
      {
	data: 'blog_agregate',
	header: 'Blog Agregate',
      },
      {
	data: 'username',
	header: 'Username',
      },
      {
	data: 'password',
	header: 'Password',
      },
    ];
var container = document.getElementById('sheet');
var hot;                    
$.getJSON("/api/supradesa", function(data){      
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
    $.post( "/api/remove_supradesa", {data:JSON.stringify(hot.getSourceDataAtRow(selected[0]))}, function(){
		location.reload();
	});
});

$("#save").click(function(){
      var data = hot.getSourceData();
      $.post( "/api/save_supradesa", {data:JSON.stringify(data)}, function(){
		location.reload();
	});
});