function makeLinkRenderer(link, text) {
  return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
    td.innerHTML = "<a href='" + link(value) + "'>" + text(value) + "</a>";
    return td;
  }
}

var columns = [{
    data: 'id',
    header: 'ID',
    renderer: makeLinkRenderer(v => "/contents/v2/" + v + "/data?sheet=null", v => v),
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
    data: 'diff_size',
    header: 'Diff',
  },
  {
    data: 'content_size',
    header: 'Content',
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
    data: 'd4',
    header: 'Data 4',
  },
  {
    data: 'd5',
    header: 'Data 5',
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

function updateQueryString(key, value, url) {
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
        hash;

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            hash = url.split('#');
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null) 
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?';
            hash = url.split('#');
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null) 
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
}

function getQueryStringValue (key) {  
  return decodeURIComponent(window.location.search.replace(new RegExp("^(?:.*[&\\?]" + encodeURIComponent(key).replace(/[\.\+\*]/g, "\\$&") + "(?:\\=([^&]*))?)?.*$", "i"), "$1"));  
}  

var getUrl = function () {
  var params = {};
  var filter = $("[name='desa-filter']").val();
  if (filter) {
    if (parseInt(filter))
      params["desa_id"] = filter;
    else
      params["domain"] = filter;
  }
  var type_filter = $("[name='type']").val();
  if (type_filter) {
    params["type"] = type_filter;
  }
  var page = $("[name='page']").val();
  params["page"] = page;

  var url = window.location.href;
  url = updateQueryString("q", filter, url);
  url = updateQueryString("type", type_filter, url);
  url = updateQueryString("page", page, url);
  window.history.replaceState({path:url},'',url);
  return "/api/contents/v2?" + $.param(params);
}

var filter = function () {
  var url = getUrl();
  $("#filter-form").attr("disabled", "disabled");
  $("#sheet").hide();
  $.getJSON(url, function (data) {
    hot.loadData(data);
    $("#filter-form").removeAttr("disabled");
    $("#sheet").show();
    setTimeout(() => hot.render(), 0);
  });
};

$("#filter-form").submit(function () {
  filter();
  return false;
});

$("#filter-form select").change(function () {
  filter();
});

$("#filter-form [name='page']").change(function (e) {
  filter();
});

$(function(){
    $("[name='desa-filter']").val(getQueryStringValue("q"));
    $("[name='type']").val(getQueryStringValue("type"));
    var page = getQueryStringValue("page");
    if(page){
        $("[name='page']").val(page);
    }
    $.getJSON(getUrl(), function (data) {
      var container = document.getElementById('sheet');
      hot = new Handsontable(container, {
        data: data,
        columns: columns,
        rowHeaders: true,
        renderAllRows: false,
        colHeaders: columns.map(c => c.header),
      });
      setTimeout(() => hot.render(), 0);
    });
});
