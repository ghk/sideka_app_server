import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-timeline',
    templateUrl: '../templates/progress-timeline.html',
})

export class ProgressTimelineComponent implements OnInit, OnDestroy {

    @Input() type: string;

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
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel.toLocaleString('id-ID');;
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
        }
    };
    chartType: string = 'line';

    progress: Progress;

    constructor(
        private _zone: NgZone,
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        let query: Query = {
        };

        let transferredDdsDataset = {
            label: 'Penyaluran DDS',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let transferredAddDataset = {
            label: 'Penyaluran ADD',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let transferredPbhDataset = {
            label: 'Penyaluran PBH',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let realizedSpendingDataset = {
            label: 'Realisasi Desa',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

        this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];
        this.rDatasets = [realizedSpendingDataset];

        this._dataService.getProgressTimelines(query, this.progressListener.bind(this)).subscribe(
            results => {                
                results.forEach(result => {
                    transferredDdsDataset.data[result.month - 1] += result.transferred_dd;
                    transferredAddDataset.data[result.month - 1] += result.transferred_add;
                    transferredPbhDataset.data[result.month - 1] += result.transferred_pbh;
                    realizedSpendingDataset.data[result.month - 1] += result.realized_spending;
                })
                this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];
                this.rDatasets = [realizedSpendingDataset];
            },
            error => { }
        );
    }

    ngOnDestroy(): void {
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
