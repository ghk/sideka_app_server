import { Component, OnInit, OnDestroy } from '@angular/core';
import { DataService } from '../services/data';

@Component({
  selector: 'sk-transfer',
  templateUrl: '../templates/transfer-recapitulation.html',
})

export class TransferRecapitulationComponent implements OnInit, OnDestroy {

    entities: any = [];
    isLoading: boolean = true;
    total: any = {
        TransferedDd: 1000,
        RealizedDd: 500,
        BudgetedDd: 1500
    }

    constructor(
        private dataService: DataService
    ) { }

    ngOnInit(): void {
        this.getBundle();
    }

    ngOnDestroy(): void {

    }
    
    getBundle() {
        let ctrl = this;
        this.dataService.getTransferBundle().subscribe(
            bundle => {
                this.entities = bundle;
                this.isLoading = false;
            },
            error => {

            }
        )
    }
}
