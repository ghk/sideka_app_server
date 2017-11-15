from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionModelSchema


class Penduduk(BaseModel):
    __tablename__ = 'penduduks'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String)
    nik = db.Column(db.String)
    nama_penduduk = db.Column(db.String)
    jenis_kelamin = db.Column(db.String)
    tempat_lahir = db.Column(db.String)
    tanggal_lahir = db.Column(db.Date)
    status_kawin = db.Column(db.String)
    agama = db.Column(db.String)
    golongan_darah = db.Column(db.String)
    kewarganegaraan = db.Column(db.String)
    no_kk = db.Column(db.String)
    nama_ayah = db.Column(db.String)
    nama_ibu = db.Column(db.String)
    hubungan_keluarga = db.Column(db.String)
    nama_dusun = db.Column(db.String)
    rw = db.Column(db.String)
    rt = db.Column(db.String)
    alamat_jalan = db.Column(db.String)
    no_telepon = db.Column(db.String)
    email = db.Column(db.String)
    no_akta = db.Column(db.String)
    no_kitas = db.Column(db.String)
    no_paspor = db.Column(db.String)
    pendidikan = db.Column(db.String)
    pekerjaan = db.Column(db.String)
    etnis_suku = db.Column(db.String)
    status_tinggal = db.Column(db.String)
    akseptor_kb = db.Column(db.String)
    cacat_fisik = db.Column(db.String)
    cacat_mental = db.Column(db.String)
    wajib_pajak = db.Column(db.String)
    lembaga_pemerintahan = db.Column(db.String)
    lembaga_kemasyarakatan = db.Column(db.String)
    lembaga_ekonomi = db.Column(db.String)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('penduduks_ix_fk_region_id', 'fk_region_id'),
    )


class PendudukModelSchema(ma.ModelSchema):
    class Meta:
        model = Penduduk
        include_fk = True

    tanggal_lahir = ma.DateTime(format='%d/%m/%Y', allow_none=True)
    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class PendudukModelSchemaIso(ma.ModelSchema):
    class Meta:
        model = Penduduk
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class PendudukReference:
    jenis_kelamin = ['Laki-Laki', 'Perempuan', 'Tidak Diketahui']
    pendidikan = ['Belum masuk TK/Kelompok Bermain',
                  'Sedang TK/Kelompok Bermain',
                  'Sedang SD/sederajat',
                  'Sedang SLTP/sederajat',
                  'Sedang SLTA/sederajat',
                  'Sedang D-1/sederajat',
                  'Sedang D-2/sederajat',
                  'Sedang D-3/sederajat',
                  'Sedang S-1/sederajat',
                  'Sedang S-2/sederajat',
                  'Sedang S-3/sederajat',
                  'Tamat SD/sederajat',
                  'Tamat SLTP/sederajat',
                  'Tamat SLTA/sederajat',
                  'Tamat D-1/sederajat',
                  'Tamat D-2/sederajat',
                  'Tamat D-3/sedarajat',
                  'Tamat D-4/sederajat',
                  'Tamat S-1/sederajat',
                  'Tamat S-2/sederajat',
                  'Tamat S-3/sederajat',
                  'Sedang SLB A/sederajat',
                  'Sedang SLB B/sederajat',
                  'Sedang SLB C/sederajat',
                  'Tamat SLB A/sederajat',
                  'Tamat SLB B/sederajat',
                  'Tamat SLB C/sederajat',
                  'Tidak pernah sekolah',
                  'Tidak dapat membaca dan menulis huruf Latin/Arab',
                  'Tidak tamat SD/sederajat']
    pendidikan_group = {
        "Tidak Diketahui": ['Tidak Diketahui', 'Belum masuk TK/Kelompok Bermain',
                            'Tidak dapat membaca dan menulis huruf Latin/Arab',
                            'Tidak pernah sekolah',
                            'Tidak tamat SD/sederajat', 'Sedang SD/sederajat'],
        "Tamat SD": ['Tamat SD/sederajat', 'Sedang SLTP/sederajat'],
        "Tamat SLTP": ['Tamat SLTP/sederajat', 'Sedang SLTA/sederajat'],
        "Tamat SLTA": ['Tamat SLTA/sederajat', 'Sedang D-1/sederajat', 'Sedang D-2/sederajat', 'Sedang D-3/sederajat',
                       'Sedang D-4/sederajat', 'Sedang S-1/sederajat'],
        "Tamat PT": ['Tamat D-1/sederajat', 'Tamat D-2/sederajat', 'Tamat D-3/sederajat', 'Tamat D-4/sederajat',
                     'Tamat S-1/sederajat', 'Sedang S-2/sederajat', 'Tamat S-2/sederajat', 'Sedang S-3/sederajat',
                     'Tamat S-3/sederajat']
    }
    pekerjaan = ['Ahli Pengobatan Alternatif',
                 'Akuntan',
                 'Anggota kabinet kementrian',
                 'Anggota Legislatif',
                 'Anggota mahkamah konstitusi',
                 'Apoteker',
                 'Arsitektur/Desainer',
                 'Belum Bekerja',
                 'Bidan swasta',
                 'Bupati/walikota',
                 'Buruh Harian Lepas',
                 'Buruh jasa perdagangan hasil bumi',
                 'Buruh Migran',
                 'Buruh Tani',
                 'Buruh usaha hotel dan penginapan lainnya',
                 'Buruh usaha jasa hiburan dan pariwisata',
                 'Buruh usaha jasa informasi dan komunikasi',
                 'Buruh usaha jasa transportasi dan perhubungan',
                 'Dokter swasta',
                 'Dosen swasta',
                 'Dukun Tradisional',
                 'Dukun/paranormal/supranatural',
                 'Duta besar',
                 'Gubernur',
                 'Guru swasta',
                 'Ibu Rumah Tangga',
                 'Jasa Konsultansi Managemen dan Teknis',
                 'Jasa pengobatan alternatif',
                 'Jasa penyewaan peralatan pesta',
                 'Juru Masak',
                 'Karyawan Honorer',
                 'Karyawan Perusahaan Pemerintah',
                 'Karyawan Perusahaan Swasta',
                 'Kepala Daerah',
                 'Konsultan Managemen dan Teknis',
                 'Kontraktor',
                 'Montir',
                 'Nelayan',
                 'Notaris',
                 'Pedagang barang kelontong',
                 'Pedagang Keliling',
                 'Pegawai Negeri Sipil',
                 'Pelajar',
                 'Pelaut',
                 'Pembantu rumah tangga',
                 'Pemilik perusahaan',
                 'Pemilik usaha hotel dan penginapan lainnya',
                 'Pemilih usaha informasi dan komunikasi',
                 'Pemilik usaha jasa hiburan dan pariwisata',
                 'Pemilik usaha jasa transportasi dan perhubungan',
                 'Pemilik usaha warung, rumah makan dan restoran',
                 'Pemuka Agama',
                 'Pemulung',
                 'Penambang',
                 'Peneliti',
                 'Pengacara',
                 'Pengrajin',
                 'Penrajin industri rumah tangga lainnya',
                 'Pengusaha kecil, menengah dan besar',
                 'Penyiar radio',
                 'Perangkat Desa',
                 'Perawat swasta',
                 'Petani',
                 'Peternak',
                 'Pialang',
                 'Pilot',
                 'POLRI',
                 'Presiden',
                 'Psikiater/Psikolog',
                 'Purnawirawan/Pensiunan',
                 'Satpam/Security',
                 'Seniman/artis',
                 'Sopir',
                 'Tidak Mempunyai Pekerjaan',
                 'TNI',
                 'Tukang Anyaman',
                 'Tukang Batu',
                 'Tukang Cuci',
                 'Tukang Cukur',
                 'Tukang Gigi',
                 'Tukang Jahit',
                 'Tukang Kayu',
                 'Tukang Kue',
                 'Tukang Las',
                 'Tukang Listrik',
                 'Tukang Rias',
                 'Tukang Sumur',
                 'Usaha jasa pengerah tenaga kerja',
                 'Wakil bupati',
                 'Wakil Gubernur',
                 'Wakil presiden',
                 'Wartawan',
                 'Wiraswasta']
