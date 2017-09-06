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
        transferredRevenue: number;
        realizedRevenue: number;
    }

    constructor(
        private _dataService: DataService
    ) { 
        this.total = {
            text: 'haha',
            transferredRevenue: 0,
            realizedRevenue: 0
        }
    }

    ngOnInit(): void {
        this._dataService.getProgressRecapitulations(null, this.progressListener.bind(this)).subscribe(
            result => {
                this.entities = result;
                this.entities.forEach(entity => {
                    this.total.transferredRevenue += entity.transferred_revenue;
                    this.total.realizedRevenue += entity.realized_revenue;
                })   
            },
            error => {
                console.log(error);
            }
        )
    }

    ngOnDestroy(): void {

    }   

    progressListener(progress: Progress): void {
        this.progress = progress;
    }
  
}
