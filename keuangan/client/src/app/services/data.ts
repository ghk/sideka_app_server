import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Response, RequestOptions } from '@angular/http';
import { ProgressHttp } from 'angular-progress-http';

import { Query } from '../models/query';
import { SharedService } from '../services/shared';
import { RequestHelper } from '../helpers/request';
import { environment } from '../../environments/environment';

import * as urljoin from 'url-join';

@Injectable()
export class DataService {

    private _serverUrl: any;

    constructor(
        private _http: ProgressHttp,
        private _sharedService: SharedService
    ) {
        this._sharedService.getConfig(false).subscribe(config => {
            this._serverUrl = config.serverUrl;
        });
    }

    getRegions(query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'regions'),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getRegion(regionId: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'regions', regionId),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getProgressRecapitulationsByYear(year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'progress/recapitulations/year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getProgressTimelinesByYear(year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'progress/timelines/year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getProgressTimelinesByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        if (regionId === '0')
            return this.getProgressTimelinesByYear(year, query, progressListener);

        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'progress/timelines/region', regionId, 'year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getBudgetTypes(query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'budget/types'),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getBudgetRecapitulationsByYear(year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'budget/recapitulations/year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getBudgetRecapitulationsByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        if (regionId === '0')
            return this.getBudgetRecapitulationsByYear(year, query, progressListener);

        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'budget/recapitulations/region', regionId, 'year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getSiskeudesPenerimaanByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'siskeudes/penerimaans/region', regionId, 'year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }

    getSiskeudesSppByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'siskeudes/spps/region', regionId, 'year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError)
    }


    getSiskeudesPenganggaranByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'siskeudes/penganggarans/region', regionId, 'year', year),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError);
    }

    getSiskeudesPenganggaranTotalSpendingByRegionAndYear(regionId: string, year: string, query: Query, progressListener: any): Observable<any> {
        let request = RequestHelper.generateHttpRequest(
            this._http,
            'GET',
            urljoin(this._serverUrl, 'siskeudes/penganggarans/region', regionId, 'year', year, 'spending'),
            query,
            progressListener
        );

        return request
            .map(res => res.json())
            .catch(this.handleError);
    }

    private handleError(error: Response | any) {
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            const err = body.error || JSON.stringify(body);
            errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        return Observable.throw(errMsg);
    }
}