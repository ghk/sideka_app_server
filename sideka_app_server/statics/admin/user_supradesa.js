var container = document.getElementById('sheet');
var hot;   
var region; 
$.getJSON("/api/get_region", function(response_region){
    region = response_region;
    console.log()
    var columns = [
     {
	data: 'username',
	header: 'Username',
      },
      {
	data: 'id_supradesa',
	header: 'Region Code',
    type: 'dropdown',
    source: region.map(c=>c.region_code),
      },
      {
	data: 'level',
	header: 'Level',
    type: 'dropdown',
    source: ['administrator','editor','author','contributor','subscriber'],
    width: 130,
      },
    ];
           
    $.getJSON("/api/users_supradesa", function(response){        
        var data;
        if (response.length < 1)        
            data = {};
        else{
            data = response.map(function(value){
                value.id_supradesa = region.filter(c => c.id_supradesa == value.id_supradesa).map(c=> c.region_code)[0]
                return value
            })
        }
        
        hot = new Handsontable(container, {
            data: data,
            columns: columns,
            rowHeaders: true,
            colHeaders: columns.map(c => c.header),
            outsideClickDeselects: false,
        });
        setTimeout(()=> hot.render(), 0);
    });
})



$( "#insertRow" ).click(function() {
    hot.alter("insert_row", 10);
    hot.selectCell(0, 0, 0, 0, true);
    hot.render();
});

$("#removeRow").click(function(){
	var selected = hot.getSelected();
    var data = hot.getSourceDataAtRow(selected[0]);
    var result = function(){
        data.id_supradesa = region.filter(c => c.region_code == data.id_supradesa).map(c=> c.id_supradesa)[0]
        return data
    }
    $.post( "/api/remove_users_supradesa", {data:JSON.stringify(result())}, function(){
		location.reload();
	});
});

$("#apply").click(function(){
    var source = hot.getSourceData();
	var data = source;
    var results = data.map(function(value){
        value.id_supradesa = region.filter(c => c.region_code == value.id_supradesa).map(c=> c.id_supradesa)[0]
        return value
    })
    $.post( "/api/update_users_supradesa", {data:JSON.stringify(data)}, function(){
		location.reload();
	});
});