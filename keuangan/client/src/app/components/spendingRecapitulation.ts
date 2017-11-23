import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';

@Component({
  selector: 'sk-spending-recapitulation',
  templateUrl: '../templates/spendingRecapitulation.html',
})

export class SpendingRecapitulationComponent implements OnInit, OnDestroy {

    private _entities = new BehaviorSubject<any>([]);    
    private _spendingTypes = new BehaviorSubject<any[]>([]);
    private _spendingRecapitulations = new BehaviorSubject<any[]>([]);

    @Input()
    set entities(value) {
        this._entities.next(value);
    }
    get entities() {
        return this._entities.getValue();
    }

    @Input()
    set spendingTypes(value) {
        this._spendingTypes.next(value);        
    }
    get spendingTypes() {
        return this._spendingTypes.getValue();
    }

    @Input()
    set spendingRecapitulations(value) {
        this._spendingRecapitulations.next(value);
    }
    get spendingRecapitulations() {
        return this._spendingRecapitulations.getValue();
    }
        
    order: string = 'region.parent.id';
    progress: Progress;

    constructor(
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        let spendingTypeQuery: Query = {           
        };

        let spendingRecapitulationsQuery: Query = {
            sort: 'region.id'
        };

        this._spendingTypes.subscribe(x => {
            this.transformData();
        });

        this._spendingRecapitulations.subscribe(x => {
            this.transformData();
        });

        this._dataService.getSpendingTypes(spendingTypeQuery, null).subscribe(
            result => {
                this.spendingTypes = result;                
            },
            error => {                
            }
        );

        this._dataService.getSpendingRecapitulations(true, spendingRecapitulationsQuery, this.progressListener.bind(this)).subscribe(
            result => {
                this.spendingRecapitulations = result;
            },
            error => {}
        );
    }

    transformData(): void {
        if (this.spendingTypes.length === 0 || this.spendingRecapitulations.length === 0)
            return;

        let entities = {};

        this.spendingRecapitulations.forEach(sr => {
            if (!entities[sr.region.id])
                entities[sr.region.id] = {
                    'region': sr.region,
                    'data': {},
                    'total': 0,
                    'barPercent': {}
                };

            this.spendingTypes.forEach((st, index) => {
                if (sr.type.id === st.id) {                     
                    //entities[sr.region.id]['data'][2 * index + 1] = sr.realized
                    entities[sr.region.id]['data'][sr.type.id] = sr.budgeted
                    entities[sr.region.id]['total'] += sr.budgeted                    
                }   
            });                  
        })

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

    ngOnDestroy(): void {
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
