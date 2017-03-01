var changeUrl = function(value){
    var pathName = window.location.pathname;
    var host = window.location.origin;
    var newUrl = host+ pathName +"?id="+value;
    var title = document.title
    if(value == null || value =="null"){
        if(pathName=="/home") pathName= "";
        newUrl = host +pathName;
    }else{
        if(pathName == "/")
            newUrl = host + "/home?id=" + value; 
    }
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
    var oldPath;    
    for(var i=0;i<idMEnu.length;i++){
        parser.href =  $("#"+idMEnu[i]+" a").attr("href")
        oldPath = parser.pathname;       
        if(supradesaId==null || supradesaId == "null"){
            if(oldPath=="/home") oldPath= "/";
            $("#"+idMEnu[i]+" a").attr("href",oldPath)
        }else{
            if(oldPath == "/")oldPath+="home";          
            $("#"+idMEnu[i]+" a").attr("href",oldPath+"?id="+supradesaId)
        }
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
    if (!supradesaId)supradesaId=null;
    $('#select-supradesa').val(String(supradesaId));
    changeUrlMenu(supradesaId)
});