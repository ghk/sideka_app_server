import { Component, ApplicationRef, Input } from "@angular/core";
import { Progress } from 'angular-progress-http';

@Component({
    selector: 'progress-bar',
    templateUrl: '../templates/progressBar.html'
})
export class ProgressBarComponent {
    private _isLoadingData: boolean;
    
    @Input()
    set isLoadingData(value) {
        this._isLoadingData = value;
    }
    get isLoadingData() {
        return this._isLoadingData;
    }
    
    constructor() { }

    ngOnInit(): void {
    }
}
