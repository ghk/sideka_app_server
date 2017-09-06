import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Response, RequestOptions } from '@angular/http';
import { ProgressHttp } from 'angular-progress-http';

import { Query } from '../models/query';
import { SharedService } from '../services/shared';
import { RequestHelper } from '../helpers/request';
import { environment } from '../../environments/environment';
import 'rxjs/add/observable/of';

@Injectable()
export class DataService {

  _serverUrl: any;

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
      this._serverUrl + '/api/regions',
      query,
      progressListener
    );

    return request
      .map(res => res.json())
      .catch(this.handleError)
  }

  getProgressRecapitulations(query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
      this._http,
      'GET',
      this._serverUrl + '/api/progress_recapitulations',
      query,
      progressListener
    );

    return request
      .map(res => res.json())
      .catch(this.handleError)
  }

  getProgressTimelines(query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
      this._http,
      'GET',
      this._serverUrl + '/api/progress_timelines',
      query,
      progressListener
    );
    
    return request
      .map(res => res.json())
      .catch(this.handleError)
  }

  getRegionProgressTimelines(regionId: string, query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
      this._http,
      'GET',
      this._serverUrl + '/api/progress_timelines/regions/' + regionId,
      query,
      progressListener
    );
    
    return request
      .map(res => res.json())
      .catch(this.handleError)
  }

  getSpendingTypes(query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
      this._http,
      'GET',
      this._serverUrl + '/api/spending_types',
      query,
      progressListener
    )

    return request
      .map(res => res.json())
      .catch(this.handleError)
  }

  getSpendingRecapitulations(query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
      this._http,
      'GET',
      this._serverUrl + '/api/spending_recapitulations',
      query,
      progressListener
    )

    return request
      .map(res => res.json())
      .catch(this.handleError)
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