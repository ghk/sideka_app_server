import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { SharedService} from '../services/shared';
import { Query } from '../models/query';

import 'chart.piecelabel.js';

@Component({
    selector: 'sk-spending-chart',
    templateUrl: '../templates/spendingChart.html',
})
export class SpendingChartComponent implements OnInit, OnDestroy {

    private _subscription: Subscription;

    region: any;
    private _sData = new BehaviorSubject<any[]>([]);

    @Input()
    set sData(value) {
        this._sData.next(value);
    }
    get sData() {
        return this._sData.getValue();
    }

    labels: any[] = [];
    colors: any =  [{ 
        backgroundColor: [
            "#FF6384",
            "#4BC0C0",
            "#FFCE56",
            "#E7E9ED",
            "#36A2EB"
        ],        
    }];
    options: any = {     
        tooltips: {
            callbacks: {
                label: function (tooltipItem, data) {
                    let dataLabel = data.labels[tooltipItem.index];
					let value: any = ': ' + data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].toLocaleString('id-ID');
					if (Array.isArray(dataLabel)) {
						dataLabel = dataLabel.slice();
						dataLabel[0] += value;
					} else {
						dataLabel += value;
					}
					return dataLabel;          
                }
            }
        }, 
        pieceLabel: {
            render: 'percentage',
            arc: true,
            position: 'outside',
            precision: 2
        },
        aspectRatio: 1
    };
    chartType: string = 'pie';

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

    getData(): void {
        let query: Query = {
        };

        this._dataService.getSpendingTypes(null, null).subscribe((types: any[]) => {
            this.labels = types.map(type => { return type.name });
            this._dataService.getSpendingRecapitulationsByRegion(this.region.id, query, this.progressListener.bind(this)).subscribe(
                results => {
                    let data = new Array(this.labels.length).fill(0);
                    results.forEach(result => {                                                                                                  
                        let dataIndex = this.labels.indexOf(result.type.name);
                        if (dataIndex === -1)
                            return;
                        data[dataIndex] += result.budgeted;
                        this.sData = data;
                    })                
                },
                error => { }
            );
        });        
    }

    ngOnDestroy(): void {
        this._subscription.unsubscribe();
    }
   
    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
