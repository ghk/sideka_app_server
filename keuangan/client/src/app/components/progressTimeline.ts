import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { SharedService} from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-timeline',
    templateUrl: '../templates/progressTimeline.html',
})
export class ProgressTimelineComponent implements OnInit, OnDestroy {

    private _subscription: Subscription; 

    progressTimelines: any; 
    region: any;
    progress: Progress;
    year: any = new Date().getFullYear();

    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {       
        this._subscription = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        });
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
    }

    getData(): void {
        let progressTimelinesQuery: Query = {
        };

        this._dataService.getProgressTimelinesByRegionAndYear(this.region.id, this.year, progressTimelinesQuery, this.progressListener.bind(this))
            .subscribe(
            results => {
                this.progressTimelines = results;                
            },  
            error => { }
        );
    }
   
    progressListener(progress: Progress): void {
        this.progress = progress;
    }
}
