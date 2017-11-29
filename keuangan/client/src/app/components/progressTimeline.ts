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

    region: any;
    private _tDatasets = new BehaviorSubject<any[]>([]);
    private _rDatasets = new BehaviorSubject<any[]>([]);
    
    private _totalBudgetedDDS: number = 0;
    private _totalBudgetedADD: number = 0;
    private _totalBudgetedPBH: number = 0;
    private _totalBudgetedSpending: number = 0;

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
                    return tooltipItem.yLabel.toLocaleString('id-ID') + '%';
                }
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    callback: function (value, index, values) {
                        return value.toLocaleString('id-ID') + '%';
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
        this._subscription = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        });
    }

    async getData(): Promise<void> {
        let year = new Date().getFullYear().toString();

        let budgetTypeQuery: Query = {
            data: {
                is_revenue: true
            }
        };

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
        };

        this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];
        this.rDatasets = [realizedSpendingDataset];

        let budgetTypes = await this._dataService.getBudgetTypes(budgetTypeQuery, null).toPromise();
        let budgetRecapitulations = await this._dataService
            .getBudgetRecapitulationsByRegionAndYear(this.region.id, year, null, null)
            .toPromise();
        this._totalBudgetedSpending = await this._dataService
            .getSiskeudesPenganggaranTotalSpendingByRegionAndYear(this.region.id, year, null, null)
            .toPromise();

        budgetRecapitulations.forEach(br => {
            budgetTypes.forEach(bt => {
                if (bt.id !== br.fk_type_id)
                    return;
                if (bt.code === 'DDS')
                    this._totalBudgetedDDS += br.budgeted;
                if (bt.code === 'ADD')
                    this._totalBudgetedADD += br.budgeted;
                if (bt.code === 'PBH')
                    this._totalBudgetedPBH += br.budgeted;
            });
        });

        this._dataService.getProgressTimelinesByRegionAndYear(this.region.id, year, query, this.progressListener.bind(this)).subscribe(
            results => {
                results.forEach(result => {                                        
                    transferredDdsDataset.data[result.month - 1] += result.transferred_dds;
                    transferredAddDataset.data[result.month - 1] += result.transferred_add;
                    transferredPbhDataset.data[result.month - 1] += result.transferred_pbh;
                    realizedSpendingDataset.data[result.month - 1] += result.realized_spending;                    
                })                

                this.transformData(transferredDdsDataset.data, this._totalBudgetedDDS);
                this.transformData(transferredAddDataset.data, this._totalBudgetedADD);
                this.transformData(transferredPbhDataset.data, this._totalBudgetedPBH);
                this.transformData(realizedSpendingDataset.data, this._totalBudgetedSpending);

                this.tDatasets = [transferredDdsDataset, transferredAddDataset, transferredPbhDataset];                
                this.rDatasets = [realizedSpendingDataset];
            },
            error => { }
        );
    }

    transformData(data: number[], total: number): void {
        var currentValue = 0;       
        data.forEach((datum, index) => {
            if (datum) {
                data[index] = datum / total * 100;
                if (data[index] < currentValue) 
                    data[index] = currentValue;                
                currentValue = data[index];
            }
        });
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
    }
   
    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
