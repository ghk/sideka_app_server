import { Component, OnInit, OnDestroy, Pipe, PipeTransform } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Pipe({
    name: 'formatCurrency',
    pure: true
})
export class FormatCurrencyPipe implements PipeTransform {
    transform(item: number, fractionSize: number): any {        
        if (isNaN(item))
            return item;
        if (item === 0)
            return "0";

        if(!fractionSize || fractionSize < 0)
            fractionSize = 1;

        let abs = Math.abs(item);
        let rounder = Math.pow(10,fractionSize);
        let isNegative = item < 0;
        let key = '';
        let powers = [
            {key: "Quantiliun", value: Math.pow(10,15)},
            {key: "Trilyun", value: Math.pow(10,12)},
            {key: "Milyar", value: Math.pow(10,9)},
            {key: "Juta", value: Math.pow(10,6)},
            {key: "Ribu", value: 1000}
        ];

        for(let i = 0; i < powers.length; i++) {
            let reduced = abs / powers[i].value;
            reduced = Math.round(reduced * rounder) / rounder;
            if (reduced >= 1) {
                abs = reduced;
                key = powers[i].key;
                break;
            }
        }

        return (isNegative ? '-' : '') + abs + ' ' + key;
    }
}

@Component({
    selector: 'sk-progress-recapitulation',
    templateUrl: '../templates/progress-recapitulation.html',
})
export class ProgressRecapitulationComponent implements OnInit, OnDestroy {
    
    entities: any = [];
    progress: Progress;
    total: {
        text: string;
        budgetedRevenue: number;
        transferredRevenue: number;
        realizedSpending: number;
    }

    constructor(
        private _route: ActivatedRoute,
        private _dataService: DataService,
        private _sharedService: SharedService
    ) {
        this.total = {
            text: 'haha',
            budgetedRevenue: 0,
            transferredRevenue: 0,
            realizedSpending: 0
        }
    }

    ngOnInit(): void {
        let query: Query = {
            sort: 'region.name'
        }

        this._dataService.getProgressRecapitulations(query, this.progressListener.bind(this)).subscribe(
            result => {
                this.entities = result;
                this.entities.forEach(entity => {
                    this.total.budgetedRevenue += entity.budgeted_revenue;
                    this.total.transferredRevenue += entity.transferred_revenue;
                    this.total.realizedSpending += entity.realized_spending;
                })
            },
            error => {
                console.log(error);
            }
        )
    }

    ngOnDestroy(): void {
    }

    getBarPercent(numerator, denominator) {
        return {
            'width': (numerator / denominator) * 100 + '%'
        };
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
