import { Component, OnInit, OnDestroy } from '@angular/core';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'hideBudgetDetail',
    pure: true
})
export class HideBudgetDetailPipe implements PipeTransform {
    transform(items: any[], filter: Object): any {
        if (!items || !filter) {
            return items;
        }
        let results = items.filter(item => 
		!item.harga_satuan && !item.harga_satuan_pak &&
		(  (item.kode_rekening && item.kode_rekening.startsWith("4") && item.kode_rekening.split(".").length <= 3)
		|| !item.kode_rekening || item.kode_rekening == "5"
		|| (item.kode_rekening && item.kode_rekening.startsWith("6") && item.kode_rekening.split(".").length <= 3))
	);
	return results;
    }
}

@Pipe({
    name: 'budgetType',
    pure: true
})
export class BudgetTypePipe implements PipeTransform {
    transform(items: any[], type: Object): any {
        if (!items || !type) {
            return items;
        }
        let results = items.filter(item => (type == '5' && !item.kode_rekening ) || (item.kode_rekening && item.kode_rekening.startsWith(type)));
        return results;
    }
}

@Component({
    selector: 'sk-spending-detail',
    templateUrl: '../templates/spending-detail.html',
})

export class SpendingDetailComponent implements OnInit, OnDestroy {

    region: any;
    is_pak: boolean = false;
    progress: Progress;
    entities: any[] = [];
    hideBudgetDetail: boolean = true;
    budgetType = "5";
    budgetTypeNames = {
        "4": "PENDAPATAN",
        "5": "BELANJA",
        "6": "PEMBIAYAAN",
    };

    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) {

    }

    ngOnInit(): void {
        this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        })
    }

    getData() {
        let penganggaranQuery: Query = {
            sort: 'row_number'
        }

        this._dataService.getRegion(this.region.id, null, null).subscribe(result => {
            this.region = result
        })

        this._dataService
            .getSiskeudesPenganggaranByRegion(this.region.id, penganggaranQuery, this.progressListener.bind(this))
            .subscribe(
            result => {
                this.entities = result
                this.transformData(this.entities);
            },
            error => {
            }
            )
    }

    ngOnDestroy(): void {
    }

    transformData(entities): void {
        /*
        this.entities.forEach(entity => {            
            if (entity.jumlah_satuan || entity.harga_satuan) {
                entity.anggaran += entity.jumlah_satuan * entity.harga_satuan;
            }
            if (entity.jumlah_satuan_pak || entity.harga_satuan_pak) {
                entity.anggaran_pak += entity.jumlah_satuan_pak * entity.harga_satuan_pak;
            }
            
            if (entity.anggaran_pak) {
                this.is_pak = true;                
                entity.perubahan = entity.anggaran_pak - entity.anggaran;                                
            }
        });

        this.entities.forEach(entity => {
            if (entity.satuan) {
                this.recursiveSum(entities, entity.kode_rekening, entity.kode_kegiatan,
                    entity.row_number, entity.anggaran, entity.anggaran_pak);
            }
        });*/

        this.entities.forEach(entity => {
            let rekeningDepth = entity.kode_rekening.split('.').length - 1;
            if (entity.kode_kegiatan && entity.kode_kegiatan.length){
                rekeningDepth += entity.kode_kegiatan.split('.').length - 2;
            }
            if (rekeningDepth < 0)
                return;
            let append = '&nbsp;'.repeat(rekeningDepth * 4);
	    entity.append = append;
        }); 
    }

    recursiveSum(entities, kode_rekening, kode_kegiatan, row_number, value, value_pak): void {        
        let new_kode_rekening = kode_rekening.split('.').slice(0, -1).join('.');  
        let new_kode_kegiatan = kode_kegiatan.split('.').slice(0, -1).join('.');
        if (!new_kode_rekening)
            return;                
        
        let filtered_entities = entities.filter(entity => entity.kode_rekening === new_kode_rekening);                
        let filtered_kegiatan_entites = entities.filter(entity => entity.kode_kegiatan && entity.kode_kegiatan === kode_kegiatan);
        let ent = this.findNearestEntity(row_number, filtered_entities, false);        
        let kegiatan_ent = this.findNearestEntity(row_number, filtered_kegiatan_entites, true); 
        if (ent) {  
            if (!ent.anggaran)
                ent.anggaran = 0;
            if (!ent.anggaran_pak)
                ent.anggaran_pak = 0;        
            ent.anggaran += value;
            ent.anggaran_pak += value_pak;        
        }

        if (kegiatan_ent) {
            console.log(filtered_kegiatan_entites);
            console.log(kegiatan_ent);
            if (!kegiatan_ent.anggaran)
                kegiatan_ent.anggaran = 0;
            if (!kegiatan_ent.anggaran_pak)
                kegiatan_ent.anggaran_pak = 0;        
            kegiatan_ent.anggaran += value;
            kegiatan_ent.anggaran_pak += value_pak;        
        }

        this.recursiveSum(entities, new_kode_rekening, new_kode_kegiatan, row_number, value, value_pak);
    }

    findNearestEntity(row_number, entities, is_kegiatan) {        
        let current = entities[0];
        entities.forEach(ent => {
            if (is_kegiatan && ent.kode_rekening === '' && ent.row_number < row_number && ent.row_number > current.row_number)
                current = ent;
            if (!is_kegiatan && ent.row_number < row_number && ent.row_number > current.row_number)
                current = ent;            
        });
        return current;
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
