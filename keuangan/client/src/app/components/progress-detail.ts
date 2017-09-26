import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-detail',
    templateUrl: '../templates/progress-detail.html',
})

export class ProgressDetailComponent implements OnInit, OnDestroy {

    private _routeSubscription: Subscription;

    regionId: string;
    region: any;
    totalRevenue: number = 0;
    totalSpending: number = 0;
    revenues: any[] = [];
    spendings: any[] = [];
    progress: Progress;

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
        this._dataService.getRegion(this.regionId, null, null).subscribe(result => {
            this.region = result;
        })

        this._dataService
            .getSiskeudesPenerimaanByRegion(this.regionId, null, this.progressListener.bind(this))
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
            .getSiskeudesSppByRegion(this.regionId, null, this.progressListener.bind(this))
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
        this._routeSubscription.unsubscribe()
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
