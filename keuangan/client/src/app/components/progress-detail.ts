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
    revenues: any[] = [];
    realizations: any[] = [];
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
        this._dataService
            .getRegionProgressRevenues(this.regionId, null, this.progressListener.bind(this))
            .subscribe(
                results => {
                    this.revenues = results;
                },
                error => {}
        )

        this._dataService
            .getRegionProgressRealizations(this.regionId, null, this.progressListener.bind(this))
            .subscribe(
                results => {
                    this.realizations = results
                },
                error => {}
        )
    }

    ngOnDestroy(): void {
        this._routeSubscription.unsubscribe()    
    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
