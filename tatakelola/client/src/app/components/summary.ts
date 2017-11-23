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
    details: any;
    detailColumns: any;
    progress: Progress;

    constructor(dataService: DataService, private router: Router) {
        this._dataService = dataService;
        this.detailColumns = {
            penduduk: ['Desa', 'Laki-Laki', 'Perempuan', 'Petani', 'Pedagang', 'Karyawan', 'Lainnya'],
            education: ['Desa', 'Tidak Diketahui', 'SD', 'SMP', 'SMA', 'PT'],
            area: ['Desa', 'Luas Km2'],
            waters: ['Desa', 'Mata Air', 'Sistem Pipa'],
            potential: ['Desa', 'Pertanian', 'Perkebunan', 'Hutan']
        }
    }

    ngOnInit(): void {
       this.viewType = 'summary';
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
            },
            error => {
                console.log(error);
            }
        )
    }

    loadDetail(type): boolean {
        this.details = [];
        switch(type) {
            case 'penduduk':
                    this.summaries.forEach(summary => {
                        let rows = [summary.region.name, summary.penduduk_sex_male, summary.penduduk_sex_female, summary.penduduk_job_petani, summary.penduduk_job_pedagang, summary.penduduk_job_karyawan, summary.penduduk_job_lain];
                        this.details.push({rows: rows});
                    });
                break;
                case 'education':
                    this.summaries.forEach(summary => {
                        let rows = [summary.region.name, summary.penduduk_edu_none, summary.penduduk_edu_sd, summary.penduduk_edu_smp, summary.penduduk_edu_sma, summary.penduduk_edu_pt];
                        this.details.push({rows: rows});
                    });
                break;
                case 'area':
                    this.summaries.forEach(summary => {
                        let rows = [summary.region.name, summary.pemetaan_desa_boundary / 1000];
                        this.details.push({rows: rows});
                    });
                case 'waters':
                    this.summaries.forEach(summary => {
                        let rows = [summary.region.name, summary.pemetaan_water_spring, summary.pemetaan_water_ditch];
                        this.details.push({rows: rows});
                    });
                    console.log(this.details);
                case 'potential':
                    this.summaries.forEach(summary => {     
                        let rows = [summary.region.name, summary.pemetaan_potential_farmland, summary.pemetaan_potential_orchard, summary.pemetaan_potential_forest]
                        this.details.push({rows: rows});
                    });
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

    goToDesa(regionId): void {
        this.router.navigateByUrl('/desa/' + regionId);
    }

    ngOnDestroy(): void {}

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
}