var changeUrl = function(value){
    var pathName = window.location.pathname;
    var host = window.location.origin;
    var newUrl = host+ pathName +"?id="+value;
    var title = document.title
    if(pathName == "/")
        newUrl = host + "/home?id=" + value; 
    changeUrlMenu(value);
    window.history.pushState(null, title, newUrl);
}

var hashUrl = function(){
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1);    
    var hash = hashes.split('=');
    if(hash[0]=="id")
        return hash[1];
    return null;
}

var changeUrlMenu = function(supradesaId){
    var idMEnu = ["dashboard","data-quality","posts-statistic","apbdes-statistic"];
    var parser = document.createElement('a');
    var oldUrl;
    
    for(var i=0;i<idMEnu.length;i++){
        parser.href =  $("#"+idMEnu[i]+" a").attr("href")
        oldUrl = parser.pathname;
        if(oldUrl =="/")oldUrl+="home";
        $("#"+idMEnu[i]+" a").attr("href",oldUrl+"?id="+supradesaId)
    }
}

$.getJSON("/api/supradesa",function(data){
    $.each(data, function (i, item) { 
        $('#select-supradesa').append($('<option>', { 
            value: item.id,
            text : item.name
        }));
    });
    var supradesaId = hashUrl();
    $('#select-supradesa').val(String(supradesaId));
    changeUrlMenu(supradesaId)
});