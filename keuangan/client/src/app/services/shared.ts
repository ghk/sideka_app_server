import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';
import 'rxjs/add/observable/of';

@Injectable()
export class SharedService {

    private _regions: ReplaySubject<any>

    constructor() { }

    getRegions(): Observable<any> {
        if (!this._regions) {
            this._regions = new ReplaySubject(1);
            this._regions.next(null);
        }
        return this._regions;
    }

}