var container = document.getElementById('sheet');
var hot;
var region;

$.getJSON("/api/regions", function (response_region) {
    region = response_region;
    console.log()
    var columns = [{
            data: 'username',
            header: 'Username',
        },
        {
            data: 'supradesa_id',
            header: 'Region Code',
            type: 'dropdown',
            source: region.map(c => c.region_code),
        },
        {
            data: 'level',
            header: 'Level',
            type: 'dropdown',
            source: ['administrator', 'editor', 'author', 'contributor', 'subscriber'],
            width: 130,
        },
    ];

    $.getJSON("/api/user_supradesas", function (response) {
        var data;
        if (response.length < 1)
            data = {};
        else {
            data = response.map(function (value) {
                value.supradesa_id = region.filter(c => c.supradesa_id == value.supradesa_id).map(c => c.region_code)[0]
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
        setTimeout(() => hot.render(), 0);
    });
})

$("#insertRow").click(function () {
    hot.alter("insert_row", 10);
    hot.selectCell(0, 0, 0, 0, true);
    hot.render();
});

$("#removeRow").click(function () {
    var selected = hot.getSelected();
    var data = hot.getSourceDataAtRow(selected[0]);
    var result = function () {
        data.supradesa_id = region.filter(c => c.region_code == data.supradesa_id).map(c => c.supradesa_id)[0]
        return data
    }
    $.delete("/api/user_supradesa", {
        data: JSON.stringify(result())
    }, function () {
        location.reload();
    });
});

$("#apply").click(function () {
    var source = hot.getSourceData();
    var data = source;
    var results = data.map(function (value) {
        value.supradesa_id = region.filter(c => c.region_code == value.supradesa_id).map(c => c.supradesa_id)[0]
        return value
    })
    $.post("/api/user_supradesas", {
        data: JSON.stringify(data)
    }, function () {
        location.reload();
    });
});