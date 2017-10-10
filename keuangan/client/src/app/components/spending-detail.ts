import { Component, OnInit, OnDestroy } from '@angular/core';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
  selector: 'sk-spending-detail',
  templateUrl: '../templates/spending-detail.html',
})

export class SpendingDetailComponent implements OnInit, OnDestroy {

    region: any;
    is_pak: boolean = false;
    progress: Progress;
    entities: any[] = [];
    
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
                    this.entities.forEach(entity => {
                        if (entity.jumlah_satuan && entity.harga_satuan)
                            entity.anggaran = entity.jumlah_satuan * entity.harga_satuan;
                        if (entity.jumlah_satuan_pak && entity.harga_satuan_pak)
                            entity.anggaran_pak = entity.jumlah_satuan_pak * entity.harga_satuan_pak;
                        if (entity.anggaran_pak) {
                            this.is_pak = true;
                            entity.perubahan = entity.anggaran_pak - entity.anggaran;
                        }

                        // remove trailing dot
                        entity.kode_rekening = entity.kode_rekening.replace(/.$/, '');
                        let rekeningDepth = entity.kode_rekening.split('.').length - 1;
                        if (rekeningDepth < 0)                        
                            return;
                        let append = '&nbsp;'.repeat(rekeningDepth * 4);      
                        entity.kode_rekening = append + entity.kode_rekening;                  
                        entity.uraian = append + entity.uraian;
                    })
                },
                error => {                    
                }
        )     
    }

    ngOnDestroy(): void {
    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
