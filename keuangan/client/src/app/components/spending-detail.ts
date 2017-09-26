import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';

@Component({
  selector: 'sk-spending-detail',
  templateUrl: '../templates/spending-detail.html',
})

export class SpendingDetailComponent implements OnInit, OnDestroy {

    private _routeSubscription: Subscription;
    
    regionId: string;   
    region: any;
    progress: Progress;
    entities: any[] = [];
    
    constructor(
        private _route: ActivatedRoute,
        private _dataService: DataService
    ) {

    }

    ngOnInit(): void {
        this._routeSubscription = this._route.params.subscribe(params => {
            this.regionId = params['regionId'];
            this.getData();
        });
    }

    getData() {  
        let siskeudesRabQuery: Query = {
            sort: 'row_number'
        }

        this._dataService.getRegion(this.regionId, null, null).subscribe(result => {
            this.region = result
        })

        this._dataService
            .getSiskeudesPenganggaranByRegion(this.regionId, null, this.progressListener.bind(this))
            .subscribe(
                result => {
                    this.entities = result                                        
                    this.entities.forEach(entity => {
                        if (entity.jumlah_satuan && entity.harga_satuan)
                            entity.anggaran = entity.jumlah_satuan * entity.harga_satuan;
                        if (entity.jumlah_satuan_pak && entity.harga_satuan_pak)
                            entity.anggaran_pak = entity.jumlah_satuan_pak * entity.harga_satuan_pak;
                        if (entity.anggaran_pak)
                            entity.perubahan = entity.anggaran_pak - entity.anggaran;

                        /*
                        let rekeningDepth = (entity.kode_rekening.match(/\./g) || []).length - 1;
                        let append = '&nbsp;'.repeat(rekeningDepth * 4);                        
                        entity.uraian = append + entity.uraian;
                        */
                    })
                },
                error => {                    
                }
        )     
    }

    ngOnDestroy(): void {
        this._routeSubscription.unsubscribe()    
    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
