var setCookie = function(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

var getCookie = function(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

$.getJSON("/api/supradesa",function(data){
    var supradesa_id = getCookie("supradesa_id")   
    if(supradesa_id == "") supradesa_id = "null";
    $.each(data, function (i, item) {        
        $('#select-supradesa').append($('<option>', { 
            value: item.id,
            text : item.name
        }));
    });
    
    $("#select-supradesa").val(supradesa_id);
});