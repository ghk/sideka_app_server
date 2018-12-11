import { Component, Input, SimpleChange, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { SharedService} from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-progress-realization-chart',
    templateUrl: '../templates/progressRealizationChart.html',
})
export class ProgressRealizationChartComponent implements OnInit, OnDestroy {

    private _subscriptions: Subscription[] = [];
    private _realizedSpendingDataset: any;
    private _totalBudgetedSpending: number = 0;
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
                    },
                    suggestedMax: 100
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
        })
    }

    async getData(): Promise<void> {
        this._realizedSpendingDataset = {
            label: 'Realisasi Desa',
            data: [null, null, null, null, null, null, null, null, null, null, null, null]
        };
        this.datasets = [this._realizedSpendingDataset];

        this._totalBudgetedSpending = await this._dataService
            .getSiskeudesPenganggaranTotalSpendingByRegionAndYear(this.region.id, this.year, null, null)
            .toPromise();
    }

    loadChart(): void {
        this._realizedSpendingDataset.data = new Array(this.labels.length).fill(null);

        this.progressTimelines.forEach(pt => {  
            this._realizedSpendingDataset.data[pt.month - 1] += pt.realized_spending;                                     
        });

        this.transformData(this._realizedSpendingDataset.data, this._totalBudgetedSpending, this.isPercentage);
        this.datasets = [this._realizedSpendingDataset];
    }

    transformData(data: number[], total: number, isPercentage: boolean): void {        
        var currentValue = 0;       
        data.forEach((datum, index) => {
            //console.log(datum, total, datum / total * 100);
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
