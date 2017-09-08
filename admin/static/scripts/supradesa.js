var columns = [
      {
            data: 'id',
            header: 'ID',
            readOnly: true,
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
      {
            data: 'zoom',
            header: 'Zoom',
      },
      {
            data: 'latitude',
            header: 'Latitude',
      },
      {
            data: 'longitude',
            header: 'Longitude',
      },
];

var container = document.getElementById('sheet');
var hot;

$.getJSON("/api/supradesas", function (data) {
      if (data.length < 1) data = {};
      hot = new Handsontable(container, {
            data: data,
            columns: columns,
            rowHeaders: true,
            colHeaders: columns.map(c => c.header),
            outsideClickDeselects: false,
      });
      setTimeout(() => hot.render(), 0);
});

$("#insertRow").click(function () {
      hot.alter("insert_row", 10);
      hot.selectCell(0, 0, 0, 0, true);
      hot.render();
});

$("#removeRow").click(function () {
      var selected = hot.getSelected();
      $.ajax({
            url: "/api/supradesas",
            type: "DELETE",            
            data: {
                  data: JSON.stringify(hot.getSourceDataAtRow(selected[0]))
            },
            contentType: "application/x-www-form-urlencoded",
            success: function () {
                  location.reload();
            }
      })
});

$("#save").click(function () {
      var data = hot.getSourceData();
      $.post("/api/supradesas", {
            data: JSON.stringify(data)
      }, function () {
            location.reload();
      });
});