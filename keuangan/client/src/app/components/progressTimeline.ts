import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
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

    region: any;
    private _tDatasets = new BehaviorSubject<any[]>([]);
    private _rDatasets = new BehaviorSubject<any[]>([]);

    @Input()
    set tDatasets(value) {
        this._tDatasets.next(value);
    }
    get tDatasets() {
        return this._tDatasets.getValue();
    }

    @Input()
    set rDatasets(value) {
        this._rDatasets.next(value);
    }
    get rDatasets() {
        return this._rDatasets.getValue();
    }

    labels: any[] = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
    options: any = {
        tooltips: {
            mode: 'index',
            callbacks: {
                label: function (tooltipItem, data) {
                    return tooltipItem.yLabel.toLocaleString('id-ID');
                }
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    callback: function (value, index, values) {
                        return value.toLocaleString('id-ID');
                    }
                }
            }]
        },
        elements: {
            line: {
                tension: 0
            }
        }
    };
    chartType: string = 'line';

    progress: Progress;

    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {       
        this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        });
    }

    getData(): void {
        let query: Query = {
        };

        let transferredDdsDataset = {
            label: 'Penyaluran DDS',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        let transferredAddDataset = {
            label: 'Penyaluran ADD',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        let transferredPbhDataset = {
            label: 'Penyaluran PBH',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        let realizedSpendingDataset = {
            label: 'Realisasi Desa',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        }

        this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];
        this.rDatasets = [realizedSpendingDataset];

        this._dataService.getProgressTimelinesByRegion(this.region.id, query, this.progressListener.bind(this)).subscribe(
            results => {
                results.forEach(result => {                                        
                    transferredDdsDataset.data[result.month - 1] += result.transferred_dds;
                    transferredAddDataset.data[result.month - 1] += result.transferred_add;
                    transferredPbhDataset.data[result.month - 1] += result.transferred_pbh;
                    realizedSpendingDataset.data[result.month - 1] += result.realized_spending;                    
                })                

                this.normalizeData(transferredDdsDataset.data);
                this.normalizeData(transferredAddDataset.data);
                this.normalizeData(transferredPbhDataset.data);
                this.normalizeData(realizedSpendingDataset.data);

                this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];
                this.rDatasets = [realizedSpendingDataset];
            },
            error => { }
        );
    }

    normalizeData(data: number[]): void {
        var currentValue = 0;       
        data.forEach((datum, index) => {
            if (datum && datum < currentValue) {
                data[index] = currentValue
            }
            currentValue = data[index];            
        })
    }

    ngOnDestroy(): void {
    }
   
    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
