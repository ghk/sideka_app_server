import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';

import { environment } from '../../environments/environment'; 

@Injectable()
export class SharedService {

    private _config: any
    private _config$: ReplaySubject<any>

    constructor() { }

    getConfig(refresh: boolean): Observable<any> {
        if (!this._config$ || refresh) {
            if (!this._config$)
                this._config$ = new ReplaySubject(1);
            this._config = environment;
            this._config$.next(this._config);
        }
        return this._config$;
    }
}