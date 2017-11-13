var columns = [
		{
	data: 'blog_id',
	header: 'Wordpress Id',
	renderer: makeLinkRenderer(function(v){ return  "/statistic/"+v }, function(v) {return v; }),
		},
		{
	data: 'domain',
	header: 'Domain',
	renderer: makeLinkRenderer(function(v){ return  "http://"+v }, function(v) {return v; }),
      },
/*
      {
	data: 'pendamping',
	header: 'Pendamping',
      },
*/
      {
	data: 'blog.score',
	header: 'Berita',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'penduduk.score',
	header: 'Penduduk',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'keuangan.score',
	header: 'Keuangan',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
	  {
	data: 'pemetaan.score',
	header: 'Pemetaan',
	type: 'numeric',
	format: '0.00',
	renderer: scoreRenderer
      },
      {
	data: 'blog.score_quality',
	header: 'B. Qlt',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'blog.score_frequency',
	header: 'B. Freq',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'penduduk.penduduk.score',
	header: 'P. Pen',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'penduduk.mutasi.score',
	header: 'P. Mut',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'penduduk.log_surat.score',
	header: 'P. Sur',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'keuangan.perencanaan.score',
	header: 'K. Ren',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'keuangan.penganggaran.score',
	header: 'K. Ang',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'keuangan.spp.score',
	header: 'K. SPP',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'keuangan.penerimaan.score',
	header: 'K. TBP',
	type: 'numeric',
	format: '0.00',
      },
	  {
	data: 'pemetaan.network_transportation.score',
	header: 'Pt. Tra',
	type: 'numeric',
	format: '0.00',
      },
	  {
	data: 'pemetaan.waters.score',
	header: 'Pt. Wat',
	type: 'numeric',
	format: '0.00',
      },
	  {
	data: 'pemetaan.facilities_infrastructures.score',
	header: 'Pt. Fac',
	type: 'numeric',
	format: '0.00',
      },
	  {
	data: 'pemetaan.boundary.score',
	header: 'Pt. Bou',
	type: 'numeric',
	format: '0.00',
      },
	  {
	data: 'pemetaan.landuse.score',
	header: 'Pt. Lan',
	type: 'numeric',
	format: '0.00',
      },
      {
	data: 'blog.last_post',
	header: 'Last Post',
      },
      {
	data: 'blog.count_24h',
	header: '#Post 1D',
      },
      {
	data: 'blog.count_1w',
	header: '#Post 1W',
      },
      {
	data: 'blog.count_30d',
	header: '#Post 30D',
      },
      {
	data: 'penduduk.last_modified',
	header: 'Penduduk Last Modified',
      },
      {
	data: 'penduduk.count',
	header: '# Penduduk',
      },
      {
	data: 'apbdes.last_modified',
	header: 'APBDes Last Modified',
      },
      {
	data: 'apbdes.count',
	header: '# APBDes',
      },
    ];
columns.forEach(function(c) {
	c.readOnly = true;
});

function makeLinkRenderer(link, text){
	return function linkRenderer(instance, td, row, col, prop, value, cellProperties) {
		td.innerHTML = "<a href='"+link(value)+"'>"+text(value)+"</a>";
		return td;
	}
}

function scoreRenderer(instance, td, row, col, prop, value, cellProperties) {
	var args = [instance, td, row, col, prop, value * 100, cellProperties];
	var bg = "red";
	var color = "white";
	if (value > 0.4){
		bg = "yellow";
		color = "black";
	}
	if (value > 0.7){
		bg = "green";
		color = "white";
	}

	Handsontable.renderers.NumericRenderer.apply(this, args);
	td.style.backgroundColor = bg;
	td.style.color = color;
};


function onSupradesaChanged(supradesaId){
	$.getJSON("/api/statistics?supradesa_id="+supradesaId, function(data){
		var container = document.getElementById('sheet');

		var hot = new Handsontable(container, {
		data: data,
		columns: columns,
		columnSorting: true,
		sortIndicator: true,
		rowHeaders: true,
		colHeaders: columns.map(function(c) { return c.header; }),
		});
		setTimeout(function(){ hot.render() }, 0);
	});	
	changeUrl(supradesaId) 
}

$('#select-supradesa').change(function(){
	var supradesaId = $(this).val();
	onSupradesaChanged(supradesaId);	
});

window.onload = function(){
	onSupradesaChanged(hashUrl());
}
