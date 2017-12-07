create view learn_kegiatan as
select 
	ang.fk_region_id , 
	r.name as region_name,
	ang.year,
	substring(ang.kode_kegiatan from 7) as kode_kegiatan , 
	substring(ang.kode_kegiatan from 7 for 2) as kode_bidang , 
	replace(lower(ang.uraian), ' ', '') as normalized_uraian,
	ang.uraian as uraian,  
	ang.anggaran,
	total_ang.total_anggaran,
	case when total_anggaran = 0 then 0 else ang.anggaran / total_ang.total_anggaran end as percentage,
	ang.pid
	from siskeudes_penganggarans ang
	inner join (
		select anggaran as total_anggaran, fk_region_id, year from siskeudes_penganggarans where kode_rekening='5'
	) total_ang on total_ang.fk_region_id = ang.fk_region_id and total_ang.year = ang.year
	inner join regions r on r.id = ang.fk_region_id
	where array_length(string_to_array(ang.kode_kegiatan, '.'), 1) - 1 = 3
	and (kode_rekening is null or kode_rekening = '')
	order by fk_region_id, kode_kegiatan;