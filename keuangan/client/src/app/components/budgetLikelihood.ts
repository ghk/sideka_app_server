import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { Pipe, PipeTransform } from '@angular/core';
import { Subscription, BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-budget-likelihood',
    templateUrl: '../templates/budgetLikelihood.html',
})
export class BudgetLikelihoodComponent implements OnInit, OnDestroy {

    private _subscriptions: Subscription[] = [];
    private _budgetLikelihoods = new BehaviorSubject<any[]>([]);

    @Input()
    set budgetLikelihoods(value) {
        this._budgetLikelihoods.next(value);
    }
    get budgetLikelihoods() {
        return this._budgetLikelihoods.getValue();
    }

    @Input() progress: any;
    region: any;

    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {
        let year = new Date().getFullYear().toString();

        this._subscriptions[0] = this._sharedService.getRegion().subscribe(region => {
            this.region = region;
            this.getData();
        });
    }

    ngOnDestroy(): void {
        this._subscriptions.forEach(sub => {
            sub.unsubscribe();
        })
    }

    getData() {
        let year = new Date().getFullYear().toString();

        let likelihoodQuery: Query = {
            sort: 'rank'
        };

        if (this.region.id === '0')
            return;

        this._dataService
            .getBudgetLikelihoodByRegionAndYear(this.region.id, year, null, null)
            .subscribe(
            result => {
                this.budgetLikelihoods = result;
            },
            error => { }
            );   
    }
}
