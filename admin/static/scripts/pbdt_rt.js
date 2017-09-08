var columns = [
     {
        header: 'Id',
        field: 'id', 
        width: 0,
        type: 'text',
        readOnly: true
    },
    {
        header: 'Kode Wilayah',
        field: 'kode_wilayah',
        width: 250,
        type: 'text'
    },
    {
        header: 'Provinsi',
        field: 'provinsi',
        width: 250,
        type: 'text'
    },
    {
        header: 'Kabupaten/Kota',
        field: 'kabupaten',
        width: 250,
        type: 'text'
    },
    {
        header: 'Kecamatan',
        field: 'kecamatan',
        width: 250,
        type: 'text'
    },
    {
        header: 'Desa/Kelurahan',
        field: 'desa_kelurahan',
        width: 250,
        type: 'text'
    },
    {
        header: 'Alamat',
        field: 'alamat',
        width: 250,
        type: 'text'
    },
    {
        header: 'Nama Kepala Rumah Tangga',
        field: 'nama_krt',
        width: 250,
        type: 'text'
    },
    {
        header: 'Jenis kelamin Kepala Rumah Tangga',
        field: 'jenis_kelamin',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Laki - laki'
            },{
                id: 2,
                label: 'Perempuan'
            }]
        },
        width: 250
    },
    {
        header: 'Umur Kepala Rumah Tangga saat pendataan',
        field: 'umur',
        width: 250,
        type: 'text'
    },
    {
        header: 'Jenjang pendidikan tertinggi',
        field: 'jenjang_pendidikan_tertinggi',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'SD/SDLB'
            },{
                id: 2,
                label: 'Paket A'
            },{
                id: 3,
                label: 'M. Ibtidaiyah'
            },{
                id: 4,
                label: 'SMP/SMPLB'
            },{
                id: 5,
                label: 'Paket B'
            },{
                id: 6,
                label: 'M. Tsanawiyah'
            },{
                id: 7,
                label: 'SMA/SMK/SMALB'
            },{
                id: 8,
                label: 'M. Aliyah'
            },{
                id: 9,
                label: 'Paket C'
            },{
                id: 10,
                label: 'Perguruan Tinggi'
            }]
        },
        width: 250
    },
    {
        header: 'Lapangan usaha dari pekerjaan utama',
        field: 'lapangan_usaha',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Pertanian tanaman padi & palawija'
            },{
                id: 2,
                label: 'Hortikultura'
            },{
                id: 3,
                label: 'Perkebunan'
            },{
                id: 4,
                label: 'Perikanan tangkap'
            },{
                id: 5,
                label: 'Perikanan budidaya'
            },{
                id: 6,
                label: 'Peternakan'
            },{
                id: 7,
                label: 'Kehutanan & pertanian lainnya'
            },{
                id: 8,
                label: 'Pertambangan/penggalian'
            },{
                id: 9,
                label: 'Industri pengolahan'
            },{
                id: 10,
                label: 'Listrik dan gas'
            },{
                id: 11,
                label: 'Bangunan/Konstruksi'
            },{
                id: 12,
                label: 'Perdagangan'
            },{
                id: 13,
                label: 'Hotel & Rumah makan'
            },{
                id: 14,
                label: 'Transportasi & Pergudangan'
            },{
                id: 15,
                label: 'Informasi & Komunaksi'
            },{
                id: 16,
                label: 'Keuangan & asuransi'
            },{
                id: 17,
                label: 'Jasa pendidikan'
            },{
                id: 18,
                label: 'Jasa kesehatan'
            },{
                id: 19,
                label: 'Jasa kemasyarakatan, pemerintahan & perorangan'
            },{
                id: 20,
                label: 'Pemulung'
            },{
                id: 21,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Status kedudukan dalam pekerjaan utama',
        field: 'status_kedudukan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Berusaha sendiri'
            },{
                id: 2,
                label: 'Berusaha dibantu buruh tidak tetap/tidak dibayar'
            },{
                id: 3,
                label: 'Berusaha dibantu buruh tetap/dibayar'
            },{
                id: 4,
                label: 'Buruh/karyawan/pegawai swasta'
            },{
                id: 5,
                label: 'PNS/TNI/Polri/BUMN/BUMD/anggota legislatif'
            },{
                id: 6,
                label: 'Pekerja bebas pertanian'
            },{
                id: 7,
                label: 'Pekerja bebas non-pertanian'
            },{
                id: 8,
                label: 'Pekerja keluarga/tidak dibayar'
            }]
        },
        width: 250
    },
    {
        header: 'Status bangunan tempat tinggal',
        field: 'status_bangunan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Milik sendiri'
            }, {
                id: 2,
                label: 'Kontrak/sewa'
            },{
                id: 3,
                label: 'Bebas sewa'
            },{
                id: 4,
                label: 'Dinas'
            },{
                id: 5,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Status Lahan',
        field: 'status_lahan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Milik sendiri'
            },{
                id: 2,
                label: 'Milik orang lain'
            },{
                id: 3,
                label: 'Tanah negara'
            },{
                id: 4,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Luas lantai',
        field: 'luas_lantai',
        type: 'text',
        width: 250
    },
    {
        header: 'Jenis lantai terluas',
        field: 'jenis_lantai_terluas',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Marmer/granit'
            },{
                id: 2,
                label: 'Keramik'
            }, {
                id: 3,
                label: 'Parket/vinil/permadani'
            },{
                id: 4,
                label: 'Ubin/tegel/teraso'
            },{
                id: 5,
                label: 'Kayu/papan kualitas tinggi'
            },{
                id: 6,
                label: 'Semen/bata merah'
            },{
                id: 7,
                label:  'Bambu'
            },{
                id: 8,
                label: 'Kayu/papan kualitas rendah'
            },{
                id: 9,
                label: 'Tanah'
            },{
                id: 10,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Jenis dinding terluas',
        field: 'jenis_dinding_terluas',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Tembok'
            },{
                id: 2,
                label: 'Plesteran anyaman bambu/kawat'
            },{
                id: 3,
                label: 'Kayu'
            },{
                id: 4,
                label: 'Anyaman bambu'
            },{
                id: 5,
                label: 'Batang kayu'
            },{
                id: 6,
                label: 'Bambu'
            },{
                id: 7,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Kondisi dinding',
        field: 'kondisi_dinding',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Bagus/kualitas tinggi'
            },{
                id: 2,
                label: 'Jelek/kualitas rendah'
            }]
        },
        width: 250
    },
    {
        header: 'Jenis atap terluas',
        field: 'jenis_atap_terluas',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Beton/genteng betoni'
            },{
                id: 2,
                label: 'Genteng keramik'
            },{
                id: 3,
                label: 'Genteng metal'
            },{
                id: 4,
                label: 'Genteng tanah liat'
            },{
                id: 5,
                label: 'Asbes'
            },{
                id: 6,
                label: 'Seng'
            },{
                id: 7,
                label: 'Sirap'
            },{
                id: 8,
                label: 'Bambu'
            },{
                id: 9,
                label: 'Jerami/ijuk/daun daunan/rumbia'
            },{
                id: 10,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Kondisi atap',
        field: 'kondisi_atap',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Bagus/kualitas tinggi'
            },{
                id: 2,
                label: 'Jelek/kualitas rendah'
            }]
        },
        width: 250
    },
    {
        header: 'Jumlah kamar tidur',
        field: 'jumlah_kamar_tidur',
        type: 'text',
        width: 250
    },
    {
        header: 'Sumber air minum',
        field: 'sumber_air_minum',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Air kemasan bermerk'
            },{
                id: 2,
                label: 'Air isi ulang'
            },{
                id: 3,
                label: 'Leding meteran'
            },{
                id: 4,
                label: 'Leding eceran'
            },{
                id: 5,
                label: 'Sumur bor/pompa'
            },{
                id: 6,
                label: 'Sumur terlindung'
            },{
                id: 7,
                label: 'Sumur tak terlindung'
            },{
                id: 8,
                label: 'Mata air terlindung'
            },{
                id: 9,
                label: 'Mata air tak terlindung'
            },{
                id: 10,
                label: 'Air sungai/danau/waduk'
            },{
                id: 11,
                label: 'Air hujan'
            },{
                id: 12,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Cara memperoleh air minum',
        field: 'cara_memperoleh_air_minum',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Membeli eceran'
            },{
                id: 2,
                label: 'Langganan'
            },{
                id: 3,
                label: 'Tidak membeli'
            }]
        },
        width: 250
    },
    {
        header: 'Sumber penerangan utama',
        field: 'sumber_penerangan_utama',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Listrik PLN'
            },{
                id: 2,
                label: 'Listrik non PLN'
            },{
                id: 3,
                label: 'Bukan listrik'
            }]
        },
        width: 250
    },
    {
        header: 'Daya listrik terpasang',
        field: 'daya_listrik_terpasang',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: '450 watt'
            },{
                id: 2,
                label: '900 watt'
            },{
                id: 3,
                label: '1300 watt'
            },{
                id: 4,
                label: '2200 watt'
            },{
                id: 5,
                label: '> 2200 watt'
            },{
                id: 6,
                label: 'Tanpa meteran'
            }]
        },
        width: 250
    },
    {
        header: 'Bahan bakar untuk memasak',
        field: 'bahan_bakar_untuk_memasak',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Listrik'
            },{
                id: 2,
                label: 'Gas > 3 kg'
            },{
                id: 3,
                label: 'Gas 3 kg'
            },{
                id: 4,
                label: 'Gas kota/biogas'
            },{
                id: 5,
                label: 'Minyak tanah'
            },{
                id: 6,
                label: 'Briket'
            },{
                id: 7,
                label: 'Arang'
            },{
                id: 8,
                label: 'Kayu bakar'
            },{
                id: 9,
                label: 'Tidak memasak di rumah'
            }]
        },
        width: 250
    },
    {
        header: 'Penggunaan fasilitas BAB',
        field: 'penggunaan_fasilitas_bab',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Sendiri'
            },{
                id: 2,
                label: 'Bersama'
            },{
                id: 3,
                label: 'Umum'
            },{
                id: 4,
                label: 'Tidak ada'
            }]
        },
        width: 250
    },
    {
        header: 'Jenis kloset',
        field: 'jenis_kloset',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Leher angsa'
            },{
                id: 2,
                label: 'Plengsengan'
            },{
                id: 3,
                label: 'Cemplung/cebluk'
            },{
                id: 4,
                label: 'Tidak pakai'
            }]
        },
        width: 250
    },
    {
        header: 'Tempat pembuangan akhir tinja',
        field: 'tempat_pembuangan_akhir_tinja',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Tangki'
            },{
                id: 2,
                label: 'SPAL'
            },{
                id: 3,
                label: 'Lubang tanah'
            },{
                id: 4,
                label: 'Kolam/sawah/sungai/danau/laut'
            },{
                id: 5,
                label: 'Pantai/tanah lapang/kebun'
            },{
                id: 6,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Tabung gas 5,5kg atau lebih',
        field: 'tabung_gas_5_5_kg_atau_lebih',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Lemari es/kulkas',
        field: 'lemari_es',
         editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'AC',
        field: 'ac',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Pemanas air',
        field: 'pemanas_air',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Telepon rumah',
        field: 'telepon_rumah',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Televisi',
        field: 'televisi',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Emas/perhiasan/tabungan',
        field: 'emas_perhiasan_tabungan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'Komputer',
        field: 'komputer_laptop',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'Sepeda',
        field: 'sepeda',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'Sepeda motor',
        field: 'sepeda_motor',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'Mobil',
        field: 'mobil',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'Perahu',
        field: 'perahu',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    }, {
        header: 'Motor tempel',
        field: 'motor_tempel',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },{
        header: 'Perahu motor',
        field: 'motor_tempel',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Kapal',
        field: 'kapal',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Jumlah Nomor HP Aktif',
        field: 'jumlah_nomor_hp_aktif',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah TV layar datar 30inch',
        field: 'jumlah_tv_layar_datar_30_inch',
        type: 'text',
        width: 250
    },
    {
        header: 'Aset lahan',
        field: 'aset_lahan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Luas lahan',
        field: 'luas_lahan',
        type: 'text',
        width: 250
    },
    {
        header: 'Rumah di tempat lain',
        field: 'rumah_di_tempat_lain',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Jumlah Sapi',
        field: 'jumlah_sapi',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah Kerbau',
        field: 'jumlah_kerbau',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah Kuda',
        field: 'jumlah_kuda',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah Babi',
        field: 'jumlah_babi',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah Kambing',
        field: 'jumlah_kambing',
        type: 'text',
        width: 250
    },
    {
        header: 'ART memiliki usaha sendiri/bersama',
        field: 'art_memiliki_usaha_sendiri',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'KKS/KPS',
        field: 'kks_kps',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
     {
        header: 'KIP/BSM',
        field: 'kip_bsm',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'KIS/BPJS/Jamkesmas',
        field: 'kis_bpjs',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'BPJS mandiri',
        field: 'bpjs_mandiri',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Jamsostek',
        field: 'jamsostek',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Asuransi kesehatan',
        field: 'asuransi',
         editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'PKH',
        field: 'pkh',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Raskin',
        field: 'raskin',
         editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 3,
                label: 'Ya'
            },{
                id: 4,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'KUR',
        field: 'kur',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Nomor urut ART WUS',
        field: 'nomor_urut_wus',
        type: 'text',
        width: 250
    },
    {
        header: 'Usia kawin suami WUS',
        field: 'usia_kawin_suami_wus',
        type: 'text',
        width: 250
    },
    {
        header: 'Usia kawin istri WUS',
        field: 'usia_kawin_istri_wus',
        type: 'text',
        width: 250
    },
    {
        header: 'Peserta KB WUS',
        field: 'peserta_kb_wus',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya'
            },{
                id: 2,
                label: 'Tidak'
            }]
        },
        width: 250
    },
    {
        header: 'Metode Kontrasepsi WUS',
        field: 'metode_kontrasepsi_wus',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'IUD'
            },{
                id: 2,
                label: 'MOW'
            },{
                id: 3,
                label: 'MOP'
            },{
                id: 4,
                label: 'Implant'
            },{
                id: 5,
                label: 'Suntik'
            },{
                id: 6,
                label: 'Pil'
            },{
                id: 7,
                label: 'Kondom'
            },{
                id: 8,
                label: 'Tradisional'
            }]
        },
        width: 250
    },
    {
        header: 'Lama kontrasepsi tahun WUS',
        field: 'lama_kontrasepsi_tahun_wus',
        type: 'text',
        width: 250
    },
    {
        header: 'Lama kontrasepsi bulan WUS',
        field: 'lama_kontrasepsi_bulan_wus',
        type: 'text',
        width: 250
    },
    {
        header: 'Tempat pelayanan KP WUS',
        field: 'tempat_pelayanan_kb',
         editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'RS Pemerintah'
            },{
                id: 2,
                label: 'RS Swasta'
            },{
                id: 3,
                label: 'Klinik Utama/Pratama'
            },{
                id: 4,
                label: 'Prakter Dokter'
            },{
                id: 5,
                label: 'Praktek Bidan'
            },{
                id: 6,
                label: 'Puskesmas/Poskesdes/Polindes'
            },{
                id: 7,
                label: 'Pustu/Pusling/Bidan Desa'
            },{
                id: 8,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Ingin punya anak lagi WUS',
        field: 'ingin_punya_anak_lagi',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Ya, segera (kurang dari 2 tahun)'
            },{
                id: 2,
                label: 'Ya, kemudian (lebih dari 2 tahun)'
            },{
                id: 3,
                label: 'Tidak ingin punya anak lagi'
            }]
        },
        width: 250
    },
    {
        header: 'Alasan tidak KB WUS',
        field: 'alasan_tidak_kb_wus',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Sedang hamil'
            },{
                id: 2,
                label: 'Alasan fertilitas'
            },{
                id: 3,
                label: 'Tidak menyetujui KB'
            },{
                id: 4,
                label: 'Tidak tahu tentang KB'
            },{
                id: 5,
                label: 'Tidak mampu/mahal'
            },{
                id: 6,
                label: 'Ingin punya anak'
            },{
                id: 6,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Jumlah Anggota Rumah Tangga',
        field: 'jumlah_anggota_rumah_tangga',
        type: 'text',
        width: 250
    },
    {
        header: 'Jumlah Keluarga',
        field: 'jumlah_keluarga',
        type: 'text',
        width: 250
    },
    {
        header: 'Status Kesejahteraan',
        field: 'status_kesejahteraan',
        editor: 'chosen',
        renderer: customDropdownRenderer,
        chosenOptions: {
            data: [{
                id: 1,
                label: 'Gembel'
            },{
                id: 2,
                label: 'Cukup Sejahtera'
            },{
                id: 3,
                label: 'Sejahtera'
            },{
                id: 4,
                label: 'Sangat Sejahtera'
            },{
                id: 5,
                label: 'Tidak mampu/mahal'
            },{
                id: 6,
                label: 'Ingin punya anak'
            },{
                id: 6,
                label: 'Lainnya'
            }]
        },
        width: 250
    },
    {
        header: 'Nomor Urut Rumah Tangga',
        field: 'nomor_urut_rumah_tangga',
        type: 'text',
        width: 250
    },
];

var container = document.getElementById('sheet');
var hot; 

function customDropdownRenderer (instance, td, row, col, prop, value, cellProperties) {
    var selectedId;
    var optionsList = cellProperties.chosenOptions.data;
    var values = (value + "").split(",");
    
    value = [];

    for (var index = 0; index < optionsList.length; index++) {
        if (values.indexOf(optionsList[index].id + "") > -1) {
            selectedId = optionsList[index].id;
            value.push(optionsList[index].label);
        }
    }
    value = value.join(", ");
    
    Handsontable.TextCell.renderer.apply(this, arguments);
}

$('#upload').click(function(){
    var fileUploader = $('#file').prop('files');
    var form = new FormData(); 
    form.append("file", fileUploader[0]);
    
    $.ajax({
            url: '/api/upload/pbdtrt',
            type: 'POST',
            data: form,
            processData: false,
            contentType: false,
            success: function(res) {
                console.log(res);
            }
    });

});