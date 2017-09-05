import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy } from '@angular/core';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { BehaviorSubject } from 'rxjs';

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

    transferredDatasets: any[] = [];
    realizedDatasets: any[] = [];
    labels: any[] = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
    options: any = {};
    chartType: string = 'line';  

    progress: Progress;

    constructor(
        private _zone: NgZone,
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        let query: Query = {
            sort: 'month'
        };        

        let transferredDdDataset = {
            label: 'Penyaluran DD',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let transferredAddDataset = {
            label: 'Penyaluran ADD',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let transferredBhprDataset = {
            label: 'Penyaluran BHPR',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        };
        let realizedSpendingDataset = {
            label: 'Realisasi Desa',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        } 

        this._tDatasets.subscribe(x => {
            this.transferredDatasets = this.tDatasets;
        });

        this._rDatasets.subscribe(x => {
            this.realizedDatasets = this.rDatasets;
        });

        this.tDatasets = [transferredDdDataset, transferredAddDataset, transferredBhprDataset];
        this.rDatasets = [realizedSpendingDataset];          

        this._dataService.getProgressTimelines(query, this.progressListener.bind(this)).subscribe(
            results => {
                results.forEach(result => {  
                    transferredDdDataset.data[result.month-1] += result.transferred_dd;
                    transferredAddDataset.data[result.month-1] += result.transferred_add;
                    transferredBhprDataset.data[result.month-1] += result.transferred_bhpr;
                    realizedSpendingDataset.data[result.month-1] += result.realized_spending;                    
                })        
                this.tDatasets = [transferredDdDataset, transferredAddDataset, transferredBhprDataset];
                this.rDatasets = [realizedSpendingDataset];          
            },
            error => {}
        );
    }

    ngOnDestroy(): void {
    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
