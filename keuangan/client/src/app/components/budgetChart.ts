import { Component, ViewChild, Input, NgZone, OnInit, OnDestroy, SimpleChange } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';

import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

import 'chart.piecelabel.js';

@Component({
    selector: 'sk-budget-chart',
    templateUrl: '../templates/budgetChart.html',
})
export class BudgetChartComponent implements OnInit, OnDestroy {
    
    region: any;
    private _sData = new BehaviorSubject<any[]>([]);

    @Input()
    set sData(value) {
        this._sData.next(value);
    }
    get sData() {
        return this._sData.getValue();
    }

    @Input() extraOptions: any;
    @Input() budgetTypes: any[];
    @Input() budgetRecapitulations: any[];

    labels: any[] = [];
    colors: any = [{
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
    };
    chartType: string = 'pie';

    constructor() { }

    ngOnInit(): void {      
    }

    getData(): void {
        this.labels.length = 0;
        this.budgetTypes.forEach(budgetType => {
            this.labels.push(budgetType.name);
        });

        let data = new Array(this.labels.length).fill(0);
        this.budgetRecapitulations.forEach(br => {
            let dataIndex = this.labels.indexOf(br.type.name);
            if (dataIndex === -1)
                return;
            data[dataIndex] += br.budgeted;
            this.sData = data;
        });
    }

    ngOnDestroy(): void {
    }

    ngOnChanges(changes: {[propKey: string]: SimpleChange}): void {
        if (changes['budgetTypes'])
            this.budgetTypes = changes['budgetTypes'].currentValue;
        if (changes['budgetRecapitulations'])
            this.budgetRecapitulations = changes['budgetRecapitulations'].currentValue;            
        if (this.budgetTypes && this.budgetRecapitulations && 
            this.budgetTypes.length > 0 && this.budgetRecapitulations.length > 0)
            this.getData();
        if (changes['extraOptions']) {
            this.options = Object.assign(this.options, changes['extraOptions'].currentValue);
        }
    }
}
