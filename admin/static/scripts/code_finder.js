function find() {
	var query = $("#input-finder").val();
	if (!$("#is-full-search")[0].checked) {
		query = "%25" + query + "%25";
	}
	$("#result-finder tbody").html("");
	$.getJSON("/api/desas/search?q=" + query, function (desas) {
		desas.forEach(function (desa) {
			var tr = $("<tr></tr>")
			tr.append("<td>" + desa.region_code + "</td>");
			tr.append("<td>" + desa.desa + "</td>");
			tr.append("<td>" + desa.kecamatan + "</td>");
			tr.append("<td>" + desa.kabupaten + "</td>");
			tr.append("<td>" + desa.propinsi + "</td>");
			tr.appendTo("#result-finder tbody");
		});
	});
}

$("#form-finder").submit(function () {
	find();
	return false;
});