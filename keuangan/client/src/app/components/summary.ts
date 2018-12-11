import { Component, OnInit, OnDestroy, Input, SimpleChange } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Pipe, PipeTransform } from '@angular/core';
import { Subscription, BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-summary',
    templateUrl: '../templates/summary.html',
})
export class SummaryComponent implements OnInit, OnDestroy {

    private _subscriptions: Subscription[] = [];
   
    progressTimelines: any;
    budgetTypes: any;
    budgetRecapitulations: any;

    region: any;
    regionId: any;
    year: string;
    isBelanjaActive: boolean = true;
    isPendapatanActive: boolean = false;
    progress: Progress;

    extraOptions: any = {
        responsive: true,
        maintainAspectRatio: true
    }

    constructor(
        private _route: ActivatedRoute,
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {      
        this._sharedService.setState('summary');
        let routeSubscription = this._route.params.subscribe(params => {
            this.regionId = params['regionId'];     
            if (!this._sharedService.region || this._sharedService.region.id !== this.regionId)       
                this._dataService.getRegion(this.regionId, null, null).subscribe(region => {
                    this._sharedService.setRegion(region);
                })            
        });

        this.year = '2018';

        let regionSubscription = this._sharedService.getRegion().subscribe(region => {
            this.progress = null;
            this.region = region;
            this.getBelanjaData();
        });
        
        this._subscriptions.push(routeSubscription);
        this._subscriptions.push(regionSubscription);
    }

    ngOnDestroy(): void {
        this._subscriptions.forEach(sub => {
            sub.unsubscribe();
        })
    }

    getProgressTimelines(): void {
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

    getBudgetTypes(isRevenue: boolean): void {
        let budgetTypeQuery: Query = {           
            data: {
                is_revenue: isRevenue ? 'true' : ''
            }
        };

        this._dataService.getBudgetTypes(budgetTypeQuery, null).subscribe(
            result => {                
                this.budgetTypes = result;                     
            },
            error => {                
            }
        );
    }

    getBudgetRecapitulations(): void {
        this._dataService
            .getBudgetRecapitulationsByRegionAndYear(this.region.id, this.year, null, null)
            .subscribe(
                result => {
                    this.budgetRecapitulations = result;
                },
            error => {}
        );
    }

    getBelanjaData(): void {
        this.isBelanjaActive = true;
        this.getBudgetTypes(false);
        this.getBudgetRecapitulations();
        this.getProgressTimelines();
    }

    getPendapatanData(): void {
        this.isPendapatanActive = true;
        this.getBudgetTypes(true);
    }
    
    ngOnChanges(changes: {[propKey: string]: SimpleChange}): void {
    }

    onTabSelected(tab: any): void {
        if (tab.heading === 'Belanja') {
            this.getBelanjaData();
        }
        else {
            this.getPendapatanData();
        }
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
