import { Component, OnInit, OnDestroy, ViewChild, AfterViewInit } from '@angular/core';
import { DataService } from '../services/data';
import { Progress } from 'angular-progress-http';
import { Router, ActivatedRoute } from "@angular/router";

import * as _ from 'lodash';

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

    constructor(dataService: DataService, private router: Router) {
        this._dataService = dataService;
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

    ngOnInit(): void {
       this.viewType = 'summary';
       this.order = 'region.parent.id';
       this.loadSummaries();
    }

    isNumber(data): boolean {
        if(isNaN(data))
            return false;

        return true;
    }

    loadSummaries(): void {
        this._dataService.getSummaries({}, this.progressListener.bind(this)).subscribe(
            result => {
                this.summaries = result;
               
                this.summaries.forEach(summary => {
                    summary['penduduk_total'] = summary.penduduk_sex_unknown + summary.penduduk_sex_male + summary.penduduk_sex_female;
                    summary['desa_edu_total'] = summary.pemetaan_school_tk + summary.pemetaan_school_sd + summary.pemetaan_school_smp + summary.pemetaan_school_sma + summary.pemetaan_school_pt;
                    summary['desa_total_waters'] = summary.pemetaaan_water_spring + summary.pemetaan_water_ditch;
                    summary['desa_total_potential'] = summary.pemetaan_potential_farmland + summary.pemetaan_potential_forest + summary.pemetaan_potential_orchard;
                    summary['kk_not_using_electricity'] = summary.penduduk_total_kk - summary.pemetaan_electricity_house;
                });
                
                this.group();     
            },
            error => {
                console.log(error);
            }
        )
    }
    
    group(): void {
        let groups  = _.groupBy(this.summaries, 'region.parent.name');
        let keys = Object.keys(groups);
        this.summaryGroups = [];

        for(let i=0; i<keys.length; i++) {
            let desas = groups[keys[i]];
            let total_apbdes = desas.reduce((a, b) => {
                let prev = a.penganggaran_budgeted_revenue;
                let next = b.penganggaran_budgeted_revenue;

                if(isNaN(prev))
                    prev = 0
                if(isNaN(next))
                    next = 0;

                return prev + next;
            });

            let boundary_total = desas.reduce((a, b) => {
                let prev = a.pemetaan_desa_boundary;
                let next = b.pemetaan_desa_boundary;

                if(isNaN(prev))
                    prev = 0
                if(isNaN(next))
                    next = 0;

                return prev + next;
            });

            let penduduk_total = desas.reduce((a, b) => {
                let prev = a.penduduk_total;
                let next = b.penduduk_total;

                if(isNaN(prev))
                    prev = 0
                if(isNaN(next))
                    next = 0;

                return prev + next;
            });

            this.summaryGroups.push({
                kabupaten: keys[i],
                apbdes_budgeted_revenue: total_apbdes,
                pemetaan_desa_boundary: boundary_total,
                penduduk_total: penduduk_total,
                desas: desas
            });
        }

        console.log(this.summaryGroups);
        this.summaryGroups = _.groupBy(this.summaries, 'region.parent.name');
        console.log(this.summaryGroups);
    }

    loadDetail(type): void {
        this.viewType = 'detail';
        this.detailType = type;
    }

    backToSummary(): boolean {
        this.viewType = 'summary';
        this.detailType = null;
        this.order = 'region.parent.id';

        return false;
    }

    goToDesa(regionId): void {
        this.router.navigateByUrl('/desa/' + regionId);
    }

    ngOnDestroy(): void {}

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
}