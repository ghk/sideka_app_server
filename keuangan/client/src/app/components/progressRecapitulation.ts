import { Component, OnInit, OnDestroy, Pipe, PipeTransform } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';



@Component({
    selector: 'sk-progress-recapitulation',
    templateUrl: '../templates/progressRecapitulation.html',
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
