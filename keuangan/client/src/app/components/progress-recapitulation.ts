import { Component, OnInit, OnDestroy } from '@angular/core';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';

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
        private _dataService: DataService
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
