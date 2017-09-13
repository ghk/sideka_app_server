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
            .getSiskeudesRabsByRegion(this.regionId, null, this.progressListener.bind(this))
            .subscribe(
                result => {
                    this.entities = result
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
