import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';


@Component({
    selector: 'sk-progress-detail',
    templateUrl: '../templates/progressDetail.html',
})
export class ProgressDetailComponent implements OnInit, OnDestroy {

    private _subscription: Subscription;

    region: any;
    year: string;
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
        this.year = '2018';

        this._subscription = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        })
    }

    getData() {
        this._dataService
            .getSiskeudesPenerimaanByRegionAndYear(this.region.id, this.year, null, this.progressListener.bind(this))
            .subscribe(
            results => {
                this.revenues = results;
                this.revenues.forEach(revenue => {                    
                    this.totalRevenue += revenue.jumlah
                })
            },
            error => { }
        );

        this._dataService
            .getSiskeudesSppByRegionAndYear(this.region.id, this.year, null, this.progressListener.bind(this))
            .subscribe(
            results => {
                this.spendings = results
                this.spendings.forEach(spending => {
                    this.totalSpending += spending.jumlah
                })
            },
            error => { }
        );
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
