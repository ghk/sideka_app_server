import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-detail',
    templateUrl: '../templates/progress-detail.html',
})

export class ProgressDetailComponent implements OnInit, OnDestroy {

    region: any;
    totalRevenue: number = 0;
    totalSpending: number = 0;
    revenues: any[] = [];
    spendings: any[] = [];
    progress: Progress;

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
        this._dataService
            .getSiskeudesPenerimaanByRegion(this.region.id, null, this.progressListener.bind(this))
            .subscribe(
            results => {
                this.revenues = results;
                this.revenues.forEach(revenue => {                    
                    this.totalRevenue += revenue.jumlah
                })
            },
            error => { }
            )

        this._dataService
            .getSiskeudesSppByRegion(this.region.id, null, this.progressListener.bind(this))
            .subscribe(
            results => {
                this.spendings = results
                this.spendings.forEach(spending => {
                    this.totalSpending += spending.jumlah
                })
            },
            error => { }
            )
    }

    ngOnDestroy(): void {
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
