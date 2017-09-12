function makeLinkRenderer(link, text) {
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='" + link(value) + "'>" + text(value) + "</a>";
		return td;
	}
}

var columns = [
	{
		data: 'blog_id',
		header: 'W ID',
		renderer: makeLinkRenderer(v => "https://sideka.id/wp-admin/network/site-info.php?id=" + v, v => v),
		readOnly: true,
	},
	{
		data: 'kode',
		header: 'Kode',
	},
	{
		data: 'domain',
		header: 'Domain',
		renderer: makeLinkRenderer(v => "http://" + v, v => v),
		readOnly: true,
	},
	{
		data: 'latitude',
		header: 'Latitude',
		format: '0.0000000',
		type: 'numeric',
	},
	{
		data: 'longitude',
		header: 'Longitude',
		format: '0.0000000',
		type: 'numeric',
	},
	{
		data: 'is_dbt',
		header: 'DBT?',
		type: 'checkbox',
	},
	{
		data: 'is_lokpri',
		header: 'LokPri?',
		type: 'checkbox',
	},
	{
		data: 'desa',
		header: 'Desa',
		readOnly: true,
	},
	{
		data: 'kecamatan',
		header: 'Kecamatan',
		readOnly: true,
	},
	{
		data: 'kabupaten',
		header: 'Kabupaten',
		readOnly: true,
	},
	{
		data: 'propinsi',
		header: 'Propinsi',
		readOnly: true,
	},
	{
		data: 'sekdes',
		header: 'Nama Sekdes',
	},
	{
		data: 'kades',
		header: 'Nama Kades',
	},
	{
		data: 'pendamping',
		header: 'Pendamping',
	},
];

function initializeTableCount(hot, spanCount) {
	//bug on first call 
	var firstCall = true;
	var updateCount = function () {
		var all = hot.getSourceData().length;
		var filtered = hot.getData().length;
		var text = all;
		if (!firstCall && all != filtered) {
			text = filtered + " dari " + all;
		}
		spanCount.innerHTML = text + " baris";
		firstCall = false;
	}

	Handsontable.hooks.add('afterLoadData', updateCount);
	Handsontable.hooks.add('afterFilter', updateCount);
	Handsontable.hooks.add('afterChange', updateCount);
	Handsontable.hooks.add('afterRemoveRow', updateCount);
	updateCount();
}

function convertBoolean(rows, column) {
	for (var i = 0, len = rows.length; i < len; i++) {
		var val = rows[i][column]
		if (val === 0)
			val = false;
		if (val === 1)
			val = true;
		rows[i][column] = val;
	}
}

$.getJSON("/api/desas", function (desas) {
	convertBoolean(desas, 'is_dbt');
	convertBoolean(desas, 'is_lokpri');
	var container = document.getElementById('sheet');

	var hot = new Handsontable(container, {
		data: desas,
		columns: columns,
		columnSorting: true,
		sortIndicator: true,
		rowHeaders: true,
		schemaFilters: true,
		renderAllRows: false,
		dropdownMenu: ['filter_by_condition', 'filter_action_bar'],
		colHeaders: columns.map(c => c.header),
		afterChange: function (changes, source) {
			if (source != "loadData" && source != "external") {
				changes.forEach(function (change) {
					var allowedColumns = ["kode", "latitude", "longitude", "sekdes", "kades", "pendamping", "is_dbt", "is_lokpri"];
					var column = change[1];
					var value = change[3];
					var prevvalue = change[2];
					var id = hot.getDataAtCell(change[0], 0);
					console.log(column, value, prevvalue, id);
					if (id && allowedColumns.indexOf(column) >= 0 && prevvalue != value) {
						if (value === false)
							value = 0;
						if (value === true)
							value = 1;
						$("#notification").html("Menyimpan...").show();
						$.post("/api/desas/" + id, {
								column: column,
								value: value
							})
							.done(function (data) {
								$("#notification").html("Penyimpanan Berhasil");
								setTimeout(function () {
									$("#notification").hide();
								}, 1000);
							});
					}
				});
			}
		},
	});
	setTimeout(() => {
		hot.render();
		initializeTableCount(hot, $("#table-count")[0]);
	}, 0);
});

$("#btn-update-from-code").click(function () {
	console.log("updating");
	$.post("/api/desas/update_from_code", function () {
		location.reload();
	});
});

$("#btn-update-sd-desa").click(function () {
	console.log("updating");
	$.post("/api/desas", function () {
		location.reload();
	});
});

$("#btn-geocode-empty-latlong").click(function () {
	console.log("updating");
	$.post("/api/desas/empty_latlong", function () {
		location.reload();
	});
});