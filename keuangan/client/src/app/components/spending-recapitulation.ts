import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { Query } from '../models/query';

@Component({
  selector: 'sk-spending-recapitulation',
  templateUrl: '../templates/spending-recapitulation.html',
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
        
    progress: Progress;

    constructor(
        private _dataService: DataService
    ) { }

    ngOnInit(): void {
        let spendingTypeQuery: Query = {           
        };
        let spendingRecapitulationsQuery: Query = {
            sort: 'region.name'
        }

        this._spendingTypes.subscribe(x => {
            this.transformData();
        })
        this._spendingRecapitulations.subscribe(x => {
            this.transformData();
        })

        this._dataService.getSpendingTypes(spendingTypeQuery, null).subscribe(
            result => {
                this.spendingTypes = result;                
            },
            error => {                
            }
        )

        this._dataService.getSpendingRecapitulations(spendingRecapitulationsQuery, this.progressListener.bind(this)).subscribe(
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

        /*
        this.spendingRecapitulations.forEach(sr => {
            if (!entities[sr.region.id])
                entities[sr.region.id] = {
                    'region': sr.region,
                    'data': new Array(this.spendingTypes.length * 2).fill(0)
                }

            this.spendingTypes.forEach((st, index) => {
                if (sr.type.id === st.id) {                     
                    entities[sr.region.id]['data'][2 * index + 1] = sr.realized
                    entities[sr.region.id]['data'][2 * index] = sr.budgeted
                }   
            })
        })
        */
        this.spendingRecapitulations.forEach(sr => {
            if (!entities[sr.region.id])
                entities[sr.region.id] = {
                    'region': sr.region,
                    'data': new Array(this.spendingTypes.length).fill(0)
                }

            this.spendingTypes.forEach((st, index) => {
                if (sr.type.id === st.id) {                     
                    //entities[sr.region.id]['data'][2 * index + 1] = sr.realized
                    entities[sr.region.id]['data'][index] = sr.budgeted
                }   
            })
        })
        
        let result = []
        Object.keys(entities).forEach(key => {
            let data = [];
            data.push(entities[key]['region']);
            data.push(entities[key]['data']);            
            result.push(data);
        })
        
        this.entities = result;
    }

    ngOnDestroy(): void {
    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
