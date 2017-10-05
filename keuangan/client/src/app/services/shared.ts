import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';

import { environment } from '../../environments/environment'; 

@Injectable()
export class SharedService {    
    
    public region: any
    private _region$: ReplaySubject<any>
    private _config: any
    private _config$: ReplaySubject<any>
    private _state$: ReplaySubject<string>

    constructor() { 
        this._region$ = new ReplaySubject(1);          
        this._state$ = new ReplaySubject(1);
    }

    getConfig(refresh: boolean): Observable<any> {        
        if (!this._config$ || refresh) {
            if (!this._config$)
                this._config$ = new ReplaySubject(1);      
            this._config = environment;
            this._config$.next(this._config);
        }
        return this._config$;
    }

    getRegion(): Observable<any> {
        return this._region$;
    }

    setRegion(region: any): void {
        this.region = region;
        this._region$.next(region);
    }

    getState(): Observable<any> {
        return this._state$;
    }

    setState(state: string): void {
        this._state$.next(state);
    }
}