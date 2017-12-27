import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { DataService } from '../services/data';
import { Progress } from 'angular-progress-http';
import { Router, ActivatedRoute } from "@angular/router";

@Component({
    selector: 'st-summary',
    templateUrl: '../templates/summary.html'
})
export class SummaryComponent implements OnInit, OnDestroy {
    private _dataService: DataService;

    viewType: string;
    detailType: string;
    summaries: any;
    summaryGroups: any[];
    progress: Progress;
    order: string;
    query: string;
    subTitle: string;
   
    constructor(dataService: DataService, private _router: Router, private _activeRouter: ActivatedRoute) {
        this._dataService = dataService;
    }

    ngOnInit(): void {
       this.viewType = 'summary';
       this.order = 'region.parent.id';
       this.query = '';
       this.subTitle = 'Rangkuman Data Desa';
       this.progress = {
           event: null,
           percentage: 0,
           loaded: 0,
           lengthComputable: true,
           total: 0
       };
       
       this._activeRouter.params.subscribe(
           params => {
               if (params['detailType'] === 'master') {
                   this.viewType = 'summary';
                   this.detailType = null;
                   this.subTitle = 'Rangkuman Data Desa';
               }
               else {
                   this.viewType = 'detail';
                   this.detailType = params['detailType'];
                   this.setSubTitle();
               }

               this.loadSummaries();
           }
       )
    }
    
    sort(order: string): boolean {
        if (this.order.includes(order)) {
            if (this.order.startsWith('-'))
                this.order = this.order.substr(1);
            else
                this.order = '-' + this.order;
        } else {
            this.order = order;
        }

        return false;
    }

    isNumber(data): boolean {
        if(isNaN(data))
            return false;

        return true;
    }

    loadSummaries(): void {
        this.progress.percentage = 0;

        this._dataService.getSummaries({}, this.progressListener.bind(this)).subscribe(
            result => {
                this.summaries = result;
               
                this.summaries.forEach(summary => {
                    summary['penduduk_total'] = summary.penduduk_sex_unknown + summary.penduduk_sex_male + summary.penduduk_sex_female;
                    summary['desa_edu_total'] = summary.pemetaan_school_tk + summary.pemetaan_school_sd + summary.pemetaan_school_smp + summary.pemetaan_school_sma + summary.pemetaan_school_pt;
                    summary['desa_total_landuse'] = summary.pemetaan_landuse_farmland + summary.pemetaan_landuse_forest + summary.pemetaan_landuse_orchard;
                   
                });  
            },
            error => {
                console.log(error);
            }
        )
    }
    
    setSubTitle() {
        switch(this.detailType) {
            case 'area':
                this.subTitle = 'Data Desa Per Area';
            break;
            case 'apbdes':
                this.subTitle = 'Data Desa Per Anggaran';
            break;
            case 'landuse':
                this.subTitle = 'Data Desa Per Lahan';
            break;
            case 'penduduk':
                this.subTitle = 'Data Desa Per Penduduk';
            break;
            case 'education':
                this.subTitle = 'Data Desa Per Gedung Sekolah';
            break;
        }
    }

    ngOnDestroy(): void {}

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
}