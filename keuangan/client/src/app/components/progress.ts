import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';

@Component({
    selector: 'sk-progress',
    templateUrl: '../templates/progress.html',
})

export class ProgressComponent implements OnInit, OnDestroy {

    private _routeSubscription: Subscription;

    regionId: string;

    constructor(
        private _route: ActivatedRoute,
        private _dataService: DataService,
        private _sharedService: SharedService
    ) {

    }

    ngOnInit(): void {        
        this._sharedService.setState('progress');
        this._routeSubscription = this._route.params.subscribe(params => {
            this.regionId = params['regionId'];     
            if (!this._sharedService.region || this._sharedService.region.id !== this.regionId)
                this._dataService.getRegion(this.regionId, null, null).subscribe(region => {
                    this._sharedService.setRegion(region);
                })            
        });
    }

    ngOnDestroy(): void {
        this._routeSubscription.unsubscribe()
    }

}
