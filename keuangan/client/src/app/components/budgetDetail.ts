import { Component, OnInit, OnDestroy } from '@angular/core';
import { Pipe, PipeTransform } from '@angular/core';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-budget-detail',
    templateUrl: '../templates/budgetDetail.html',
})
export class BudgetDetailComponent implements OnInit, OnDestroy {

    private _subscription: Subscription;

    region: any;
    isPak: boolean = false;
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
    ) { }

    ngOnInit(): void {
        this._subscription = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        })
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
    }

    getData() {
        let year = new Date().getFullYear().toString();

        let penganggaranQuery: Query = {
            sort: 'row_number'
        };

        this._dataService.getRegion(this.region.id, null, null).subscribe(result => {
            this.region = result
        });

        this._dataService
            .getSiskeudesPenganggaranByRegionAndYear(this.region.id, year, penganggaranQuery, this.progressListener.bind(this))
            .subscribe(
            result => {
                this.entities = result
                this.transformData(this.entities);
            },
            error => {
            }
        );
    }

    transformData(entities): void {
        this.entities.forEach(entity => {
            if (!this.isPak && entity.anggaran_pak)
                this.isPak = true;

            let rekeningDepth = entity.kode_rekening.split('.').length - 1;
            if (entity.kode_kegiatan && entity.kode_kegiatan.length) {
                rekeningDepth += entity.kode_kegiatan.split('.').length - 2;
            }
            if (rekeningDepth < 0)
                return;
            let append = '&nbsp;'.repeat(rekeningDepth * 4);
            entity.append = append;
        });
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
