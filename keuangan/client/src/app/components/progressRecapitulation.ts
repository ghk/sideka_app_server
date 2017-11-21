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
            sort: 'region.id'
        }

        this._dataService.getProgressRecapitulations(query, this.progressListener.bind(this)).subscribe(
            result => {
                this.entities = result;

                for (let i = this.entities.length - 1; i >= 0; i--) {
                    if (this.entities[i].budgeted_revenue === 0 &&
                        this.entities[i].transferred_revenue === 0 &&
                        this.entities[i].realized_spending === 0)
                        this.entities.splice(i, 1);                  
                    else {
                        this.total.budgetedRevenue += this.entities[i].budgeted_revenue;
                        this.total.transferredRevenue += this.entities[i].transferred_revenue;
                        this.total.realizedSpending += this.entities[i].realized_spending;  
                    }
                }               

                this.entities.forEach(entity => {
                    entity.barPercent = {
                        "budgetedRevenue": this.getBarPercent(entity.budgeted_revenue, this.total.budgetedRevenue),
                        "transferredRevenue": this.getBarPercent(entity.transferred_revenue, entity.budgeted_revenue),
                        "realizedSpending": this.getBarPercent(entity.realized_spending, entity.budgeted_revenue)
                    }                
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
