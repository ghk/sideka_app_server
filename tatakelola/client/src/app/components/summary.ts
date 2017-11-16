import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { DataService } from '../services/data';

@Component({
    selector: 'st-summary',
    templateUrl: '../templates/summary.html'
})
export class SummaryComponent implements OnInit, OnDestroy {
    private _dataService: DataService;

    summaries: any;

    constructor(dataService: DataService) {
        this._dataService = dataService;
    }

    ngOnInit(): void {
        this._dataService.getSummaries({}, null).subscribe(
            result => {
                this.summaries = result;
            },
            error => {
                console.log(error);
            }
        )
    }

    ngOnDestroy(): void {
        
    }
}