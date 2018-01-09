import { Component, Input, SimpleChange, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { SharedService} from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-revenue-chart',
    templateUrl: '../templates/progressRevenueChart.html',
})
export class ProgressRevenueChartComponent implements OnInit, OnDestroy {

    private _subscriptions: Subscription[] = [];
    private _transferredDdsDataset: any;
    private _transferredAddDataset: any;
    private _transferredPbhDataset: any;
    private _totalBudgetedDDS: number = 0;
    private _totalBudgetedADD: number = 0;
    private _totalBudgetedPBH: number = 0;
    private _datasets = new BehaviorSubject<any[]>([]);    
    private _isPercentage = new BehaviorSubject<boolean>(true);
    
    @Input() year: any;
    @Input() progressTimelines: any;

    @Input()
    set datasets(value) {
        this._datasets.next(value);
    }
    get datasets() {
        return this._datasets.getValue();
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

    region: any;
    isFinished: boolean = false;
    
    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {      
    }

    ngOnDestroy(): void {
        this._subscriptions.forEach(sub => {
            sub.unsubscribe();
        });
    }

    async getData(): Promise<void> {
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
        this.datasets = [this._transferredDdsDataset, this._transferredAddDataset, this._transferredPbhDataset];

        let budgetTypeQuery: Query = {
            data: {
                is_revenue: true
            }
        };

        let budgetRecapitulationsQuery: Query = {
            data: {
                is_full_region: ''
            }
        }

        let budgetTypes = await this._dataService.getBudgetTypes(budgetTypeQuery, null).toPromise();
        let budgetRecapitulations = await this._dataService
            .getBudgetRecapitulationsByRegionAndYear(this.region.id, this.year, budgetRecapitulationsQuery, null)
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
    }

    loadChart(): void {
        this._transferredAddDataset.data = new Array(this.labels.length).fill(null);
        this._transferredDdsDataset.data = new Array(this.labels.length).fill(null);
        this._transferredPbhDataset.data = new Array(this.labels.length).fill(null);

        this.progressTimelines.forEach(pt => {                   
            this._transferredDdsDataset.data[pt.month - 1] += pt.transferred_dds;
            this._transferredAddDataset.data[pt.month - 1] += pt.transferred_add;
            this._transferredPbhDataset.data[pt.month - 1] += pt.transferred_pbh;
        });

        this.transformData(this._transferredDdsDataset.data, this._totalBudgetedDDS, this.isPercentage);
        this.transformData(this._transferredAddDataset.data, this._totalBudgetedADD, this.isPercentage);
        this.transformData(this._transferredPbhDataset.data, this._totalBudgetedPBH, this.isPercentage);

        this.datasets = [this._transferredDdsDataset, this._transferredAddDataset, this._transferredPbhDataset];
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

    ngOnChanges(changes: {[propKey: string]: SimpleChange}): void {        
        if (this.progressTimelines) {
            this._subscriptions[0] = this._sharedService.getRegion().subscribe(region => {
                this.region = region;            
                this.getData().then(() => {
                    this.isFinished = true;
                    this._subscriptions[1] = this._isPercentage.subscribe(isPercentage => {
                        this.loadChart(); 
                    });
                });
            });
        }
    }
}
