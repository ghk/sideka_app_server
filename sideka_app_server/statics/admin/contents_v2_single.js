schema.forEach(c => {
	c.readOnly = true;
});
var container = document.getElementById('sheet');
var search = document.location.search.split('=');
var sheet = search[search.length - 1];

if(sheet === "null"){
    var keys = Object.keys(content.data);
    if(keys.length > 0){
        sheet = keys[0];
        document.location.search = "?sheet=" + sheet;
    }
}

$('#' + sheet).addClass("active");

var data = content.data[sheet] ? content.data[sheet] : content.data;

var hot = new Handsontable(container, {
  data: data,
  columns: schema,
  rowHeaders: true,
  colHeaders: schema.map(function(c){ return c.header; }),
});

setTimeout(function() {
    hot.render();
}, 100);

function onModeChange(radio){
    var value = radio.value;
    var result = [];

    if(value === 'diffs'){
        if(content['diffs'])
            result = parseDiffs(content['diffs'][sheet]);
    }
    else{
        result = content.data[sheet];
    }

    hot.loadData(result);
}

function parseDiffs(data){
    var result = [];

    for(var i=0; i<data.length; i++){
        var diffTypes = Object.keys(data[i]);

        for(var j=0; j<diffTypes.length; j++){
            var type = diffTypes[j];
            var diff = data[i][type];

            for(var k=0; k<diff.length; k++){
                var diffItem = diff[k];
                diffItem.push(type);
                result.push(diffItem);
            }
        }
    }
    return result;
}