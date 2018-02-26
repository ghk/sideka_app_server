import * as d3 from 'd3';
import * as nv from 'nvd3';

export class ChartHelper {
    sources: any = { "genders": [], "pekerjaan": [], "pendidikan": [] }
    
    pendidikanGroups = {
        "Tidak Diketahui": ['Tidak Diketahui', 'Belum masuk TK/Kelompok Bermain', 'Tidak dapat membaca dan menulis huruf Latin/Arab','Tidak pernah sekolah',
        'Tidak tamat SD/sederajat', 'Sedang SD/sederajat'],
        "Tamat SD": ['Tamat SD/sederajat', 'Sedang SLTP/sederajat'],
        "Tamat SLTP": ['Tamat SLTP/sederajat', 'Sedang SLTA/sederajat'],
        "Tamat SLTA": ['Tamat SLTA/sederajat', 'Sedang D-1/sederajat', 'Sedang D-2/sederajat', 'Sedang D-3/sederajat',
        'Sedang D-4/sederajat', 'Sedang S-1/sederajat'],
        "Tamat PT": ['Tamat D-1/sederajat', 'Tamat D-2/sederajat', 'Tamat D-3/sederajat', 'Tamat D-4/sederajat',
        'Tamat S-1/sederajat', 'Sedang S-2/sederajat', 'Tamat S-2/sederajat', 'Sedang S-3/sederajat',
        'Tamat S-3/sederajat']
    }

    constructor() {
        this.sources.pekerjaan = ['Petani', 'Pedagang', 'Karyawan', 'Nelayan', 'Lainnya'];
        this.sources.pendidikan = ['Tamat SD', 'Tamat SMP', 'Tamat SMA', 'Tamat PT'];
    }

    getPekerjaanRaw(data: any[]): any[] {
        let result: any[] = [];
    
        for (let index in this.sources['pekerjaan']) {
            let source = this.sources['pekerjaan'][index];

            let totalMale = data.filter(e => 
               e.pekerjaan && e.pekerjaan.toLowerCase().indexOf(source.toLowerCase()) === 0 && e.jenis_kelamin === 'Laki-Laki').length;

            let totalFemale = data.filter(e => 
               e.pekerjaan && e.pekerjaan.toLowerCase().indexOf(source.toLowerCase()) === 0 && e.jenis_kelamin === 'Perempuan').length;

            let resultMale = { jenis_kelamin: 'Laki-Laki', jumlah: totalMale, pekerjaan: source };
            let resultFemale = { jenis_kelamin: 'Perempuan', jumlah: totalFemale, pekerjaan: source };

            result.push(resultMale);
            result.push(resultFemale);
        }

        return result;
    }

    getPendidikanRaw(data: any[]): any[] {
        let result: any[] = [];
        let keys = Object.keys(this.pendidikanGroups);

        for (let index in keys) {
            let key = keys[index];
            let items = this.pendidikanGroups[key];

            let totalMale = data.filter(e => e.pendidikan 
                && items.filter(f => f.toLowerCase() === e.pendidikan.toLowerCase()).length > 0
                && e.jenis_kelamin === 'Laki-Laki').length;

            let totalFemale = data.filter(e => e.pendidikan 
                && items.filter(f => f.toLowerCase() === e.pendidikan.toLowerCase()).length > 0
                && e.jenis_kelamin === 'Perempuan').length;

            let resultMale = { jenis_kelamin: 'Laki-Laki', jumlah: totalMale, pendidikan: key };
            let resultFemale = { jenis_kelamin: 'Perempuan', jumlah: totalFemale, pendidikan: key };
    
            result.push(resultMale);
            result.push(resultFemale);
        }

        return result;
    }

    transformDataStacked(raw, label): any{
        var all = {};
        var allPerSex = {}
        var total = 0;
        for(var i = 0; i < raw.length; i++){
            var r = raw[i];
            var val = parseInt(r.jumlah);
            var p = r[label].toUpperCase();
            if(!all[p])
            {
                all[p] = 0;
            }
            all[p] += val;
            if(!allPerSex[p])
            {
                allPerSex[p] ={};
            }
            allPerSex[p][r.jenis_kelamin] = val;
            total += val;
        }

        //remove values lesser than 2% of total
        var min = Math.round(0.01 * total);
        var keys = Object.keys(all);
        var filteredKeys = [];
        var etcS = {"Perempuan": 0, "Laki-Laki": 0, "Tidak Diketahui": 0};
        var etc = 0;
        for(var i = 0; i < keys.length; i++) {
            var key = keys[i];
            if(all[key] < min){
                var sexes = Object.keys(etcS);
                for(var j = 0; j < sexes.length; j++)
                {
                    var sex = sexes[j];
                    if(allPerSex[key][sex]) {
                        etcS[sex] += allPerSex[key][sex];
                    }
                }
                etc += all[key];
            } else {
                filteredKeys.push(key);
            }
        }
        if(etc > 0) {
            var etcN = "LAIN - LAIN";
            all[etcN] = etc;
            allPerSex[etcN] = etcS;
            filteredKeys.push(etcN);
        }
        var sortedPekerjaan = filteredKeys.sort(function(a, b){
                var va = all[a];
                var vb = all[b];
                return vb - va;
        });
        return ["Perempuan", "Laki-Laki", "Tidak Diketahui"].map(function(sex){
            return {
                key: sex,
                values: sortedPekerjaan
                    .map(function(p){
                        var val = allPerSex[p][sex];
                        if(!val)
                            val == 0;
                        return {"label": p, "value": val}
                    })
            }
        });
    }

    renderMultiBarHorizontalChart(id: string, data: any[]): any {
        let chart = nv.models.multiBarHorizontalChart().x(function(d) {  return d.label })
            .y(function(d) { return d.value }).margin({top: 20, right: 20, bottom: 30, left: 100})
            .stacked(true).showControls(false);
        
        chart.yAxis.tickFormat(d3.format('d'));
        d3.select('#' + id + ' svg').datum(data).call(chart);
        nv.utils.windowResize(chart.update);

        return chart;
    }
}