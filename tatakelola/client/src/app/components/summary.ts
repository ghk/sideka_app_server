import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { DataService } from '../services/data';

@Component({
    selector: 'st-summary',
    templateUrl: '../templates/summary.html'
})
export class SummaryComponent implements OnInit, OnDestroy {
    private _dataService: DataService;

    viewType: string;
    detailType: string;
    summaries: any;
    details: any;
    detailColumns: any;

    constructor(dataService: DataService) {
        this._dataService = dataService;
        this.detailColumns = {
            penduduk: ['Laki-Laki', 'Perempuan'],
            education: ['TIdak Diketahui', 'SD', 'SMP', 'SMA', 'PT']
        }
    }

    ngOnInit(): void {
       this.viewType = 'summary';
       this.loadSummaries();
    }

    loadSummaries(): void {
        this._dataService.getSummaries({}, null).subscribe(
            result => {
                this.summaries = result;
            },
            error => {
                console.log(error);
            }
        )
    }

    loadDetail(summary, type): boolean {
       switch(type) {
           case 'penduduk':
              this.details = [summary.penduduk_sex_male, summary.penduduk_sex_female];
              break;
            case 'education':
              this.details = [summary.penduduk_edu_none, summary.penduduk_edu_sd, summary.penduduk_edu_smp, summary.penduduk_edu_sma,
                 summary.penduduk_edu_pt];
              break;
       }

       this.viewType = 'detail';
       this.detailType =type;
       return false;
    }

    backToSummary(): boolean {
        this.viewType = 'summary';
        this.detailType = null;
        this.details = null;

        return false;
    }

    ngOnDestroy(): void {
        
    }
}