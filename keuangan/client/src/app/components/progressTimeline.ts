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
    private _tDatasets = new BehaviorSubject<any[]>([]);
    private _rDatasets = new BehaviorSubject<any[]>([]);    
    private _isPercentage = new BehaviorSubject<boolean>(true);

    private _progressTimelines: any;
    private _transferredDdsDataset: any;
    private _transferredAddDataset: any;
    private _transferredPbhDataset: any;
    private _realizedSpendingDataset: any;
    private _totalBudgetedDDS: number = 0;
    private _totalBudgetedADD: number = 0;
    private _totalBudgetedPBH: number = 0;
    private _totalBudgetedSpending: number = 0;
    
    region: any;

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

    @Input()
    set isPercentage(value) {
        this._isPercentage.next(value);
    }
    get isPercentage() {
        return this._isPercentage.getValue();
    }

    labels: any[] = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
    options: any = {
        tooltips: {
            mode: 'index',
            callbacks: {
                label: function (tooltipItem, data) {
                    if (this.isPercentage)
                        return tooltipItem.yLabel.toLocaleString('id-ID') + '%';
                    else
                        return tooltipItem.yLabel.toLocaleString('id-ID');
                }
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    callback: function (value, index, values) {
                        if (this.isPercentage)
                            return value.toLocaleString('id-ID') + '%';
                        else
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
        this._subscription = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        });
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
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

        this._transferredDdsDataset = {
            label: 'Penyaluran DDS',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        this._transferredAddDataset = {
            label: 'Penyaluran ADD',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        this._transferredPbhDataset = {
            label: 'Penyaluran PBH',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        this._realizedSpendingDataset = {
            label: 'Realisasi Desa',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };

        this.tDatasets = [this._transferredDdsDataset, this._transferredAddDataset, this._transferredPbhDataset];
        this.rDatasets = [this._realizedSpendingDataset];

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
                this._progressTimelines = results;                
                this._isPercentage.subscribe(isPercentage => {
                    this.loadChart(); 
                });
            },
            error => { }
        );
    }

    loadChart(): void {
        this._transferredAddDataset.data = new Array(this.labels.length).fill(null);
        this._transferredDdsDataset.data = new Array(this.labels.length).fill(null);
        this._transferredPbhDataset.data = new Array(this.labels.length).fill(null);
        this._realizedSpendingDataset.data = new Array(this.labels.length).fill(null);

        this._progressTimelines.forEach(pt => {                   
            this._transferredDdsDataset.data[pt.month - 1] += pt.transferred_dds;
            this._transferredAddDataset.data[pt.month - 1] += pt.transferred_add;
            this._transferredPbhDataset.data[pt.month - 1] += pt.transferred_pbh;
            this._realizedSpendingDataset.data[pt.month - 1] += pt.realized_spending;                    
        });

        this.transformData(this._transferredDdsDataset.data, this._totalBudgetedDDS, this.isPercentage);
        this.transformData(this._transferredAddDataset.data, this._totalBudgetedADD, this.isPercentage);
        this.transformData(this._transferredPbhDataset.data, this._totalBudgetedPBH, this.isPercentage);
        this.transformData(this._realizedSpendingDataset.data, this._totalBudgetedSpending, this.isPercentage);

        this.tDatasets = [this._transferredDdsDataset, this._transferredAddDataset, this._transferredPbhDataset];
        this.rDatasets = [this._realizedSpendingDataset];
    }

    transformData(data: number[], total: number, isPercentage: boolean): void {        
        var currentValue = 0;       
        data.forEach((datum, index) => {
            if (datum) {
                if (isPercentage)
                    data[index] = datum / total * 100;
                else
                    data[index] = datum;

                if (data[index] < currentValue) 
                    data[index] = currentValue;                
                currentValue = data[index];
            }
        });
    }   
   
    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
