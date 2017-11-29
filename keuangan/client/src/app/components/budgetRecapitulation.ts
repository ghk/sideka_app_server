import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';
import { Subscription } from 'rxjs/Subscription';

@Component({
  selector: 'sk-budget-recapitulation',
  templateUrl: '../templates/budgetRecapitulation.html',
})

export class BudgetRecapitulationComponent implements OnInit, OnDestroy {

    private _budgetType = new BehaviorSubject<string>('5');
    private _entities = new BehaviorSubject<any>([]);    
    private _budgetTypes = new BehaviorSubject<any[]>([]);
    private _budgetRecapitulations = new BehaviorSubject<any[]>([]);
    private _subscriptions: Subscription[] = [];

    @Input()
    set budgetType(value) {
        this._budgetType.next(value);
    }
    get budgetType() {
        return this._budgetType.getValue();
    }

    @Input()
    set entities(value) {
        this._entities.next(value);
    }
    get entities() {
        return this._entities.getValue();
    }

    @Input()
    set budgetTypes(value) {
        this._budgetTypes.next(value);        
    }
    get budgetTypes() {
        return this._budgetTypes.getValue();
    }

    @Input()
    set budgetRecapitulations(value) {
        this._budgetRecapitulations.next(value);
    }
    get budgetRecapitulations() {
        return this._budgetRecapitulations.getValue();
    }
        
    total: number[] = [];
    order: string = 'region.parent.id';
    progress: Progress;

    constructor(
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        let year = new Date().getFullYear().toString();

        this._subscriptions[0] = this._budgetType.subscribe(x => {
            this.getBudgetTypes();
        })

        this._subscriptions[1] = this._budgetTypes.subscribe(x => {
            this.transformData();
        });

        this._subscriptions[2] = this._budgetRecapitulations.subscribe(x => {
            this.transformData();
        });

        let budgetRecapitulationsQuery: Query = {
            sort: 'region.id',
            data: {
                is_full_region: true
            }
        };

        this._dataService
            .getBudgetRecapitulationsByYear(year, budgetRecapitulationsQuery, this.progressListener.bind(this))
            .subscribe(
            result => {
                this.budgetRecapitulations = result;
            },
            error => {}
        );
    }
    
    ngOnDestroy(): void {
        this._subscriptions.forEach(sub => {
            sub.unsubscribe();
        })
    }  

    getBudgetTypes(): void {
        let budgetTypeQuery: Query = {           
            data: {
                is_revenue: this.budgetType === '5' ? false : true
            }
        };

        this._dataService.getBudgetTypes(budgetTypeQuery, null).subscribe(
            result => {                
                this.total = new Array(result.length).fill(0);  
                this.budgetTypes = result;                     
            },
            error => {                
            }
        );
    }

    transformData(): void {       
        if (this.budgetTypes.length === 0 || this.budgetRecapitulations.length === 0)
            return;

        let entities = {};

        this.budgetRecapitulations.forEach(sr => {
            if (!entities[sr.region.id])
                entities[sr.region.id] = {
                    'region': sr.region,
                    'data': {},
                    'total': 0,
                    'barPercent': {}
                };

            this.budgetTypes.forEach((st, index) => {
                if (sr.type.id === st.id) {          
                    //entities[sr.region.id]['data'][2 * index + 1] = sr.realized
                    entities[sr.region.id]['data'][sr.type.id] = sr.budgeted;
                    entities[sr.region.id]['total'] += sr.budgeted;
                    this.total[index] += sr.budgeted;
                }   
            });                  
        });

        let result = [];        
        Object.keys(entities).forEach(key => {
            if (entities[key].total == 0) {
                delete entities[key];
            } else {
                Object.keys(entities[key].data).forEach(dataKey => {
                    entities[key].barPercent[dataKey] = this.getBarPercent(entities[key].data[dataKey], entities[key].total);                    
                })

                let data = {
                    'region': entities[key]['region'],
                    'data': entities[key]['data'],
                    'barPercent': entities[key]['barPercent']
                };
                result.push(data);
            };
        })
        
        this.entities = result;
    }
 
    getBarPercent(numerator, denominator) {
        return {
            'width': (numerator / denominator) * 100 + '%'
        };
    }

    sort(order: string) {
        if (this.order.includes(order)) {
            if (this.order.startsWith('-'))
                this.order = this.order.substr(1);
            else
                this.order = '-' + this.order;
        } else {
            this.order = order;
        }
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
