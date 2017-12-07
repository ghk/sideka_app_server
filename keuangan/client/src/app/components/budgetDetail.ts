import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { Pipe, PipeTransform } from '@angular/core';
import { Subscription, BehaviorSubject } from 'rxjs';
import { Progress } from 'angular-progress-http';
import { DataService } from '../services/data';
import { SharedService } from '../services/shared';
import { Query } from '../models/query';

@Component({
    selector: 'sk-budget-detail',
    templateUrl: '../templates/budgetDetail.html',
})
export class BudgetDetailComponent implements OnInit, OnDestroy {

    private _subscriptions: Subscription[] = [];
    private _budgetType = new BehaviorSubject<string>('5');
    private _budgetTypes = new BehaviorSubject<any[]>([]);
    private _budgetRecapitulations = new BehaviorSubject<any[]>([]);

    @Input()
    set budgetType(value) {
        this._budgetType.next(value);
    }
    get budgetType() {
        return this._budgetType.getValue();
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

    region: any;
    isPak: boolean = false;
    progress: Progress;
    entities: any[] = [];
    hideBudgetDetail: boolean = true;
    budgetTypeNames = {
        '4': 'PENDAPATAN',
        '5': 'BELANJA',
        '6': 'PEMBIAYAAN',
    };

    constructor(
        private _dataService: DataService,
        private _sharedService: SharedService
    ) { }

    ngOnInit(): void {
        let year = new Date().getFullYear().toString();

        this._subscriptions[0] = this._sharedService.getRegion().subscribe(region => {
            this.progress = null;
            this.region = region;
            this.getData();
        });

        this._subscriptions[1] = this._budgetType.subscribe(x => {
            this.getBudgetTypes();
        });
    }

    ngOnDestroy(): void {
        this._subscriptions.forEach(sub => {
            sub.unsubscribe();
        })
    }

    getData() {
        let year = new Date().getFullYear().toString();

        let penganggaranQuery: Query = {
            sort: 'row_number'
        };

        this._dataService
            .getBudgetRecapitulationsByRegionAndYear(this.region.id, year, null, null)
            .subscribe(
            result => {
                this.budgetRecapitulations = result;
            },
            error => {}
        );

        this._dataService
            .getSiskeudesPenganggaranByRegionAndYear(this.region.id, year, penganggaranQuery, this.progressListener.bind(this))
            .subscribe(
            result => {
                this.entities = result
                this.transformData(this.entities);
            },
            error => {
            }
        );
    }

    transformData(entities): void {
        this.entities.forEach(entity => {
            if (!this.isPak && entity.anggaran_pak)
                this.isPak = true;

            let rekeningDepth = entity.kode_rekening.split('.').length - 1;
            if (entity.kode_kegiatan && entity.kode_kegiatan.length) {
                rekeningDepth += entity.kode_kegiatan.split('.').length - 2;
            }
            if (rekeningDepth < 0)
                return;
            let append = '&nbsp;'.repeat(rekeningDepth * 4);
            entity.append = append;
        });
    }

    getBudgetTypes(): void {
        let budgetTypeQuery: Query = {           
            data: {
                is_revenue: this.budgetType === '5' ? false : true
            }
        };

        this._dataService.getBudgetTypes(budgetTypeQuery, null).subscribe(
            result => {                
                this.budgetTypes = result;                     
            },
            error => {                
            }
        );
    }

    progressListener(progress: Progress): void {
        this.progress = progress;
    }

}
