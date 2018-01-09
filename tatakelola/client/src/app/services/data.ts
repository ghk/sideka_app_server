import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Response, RequestOptions } from '@angular/http';
import { ProgressHttp } from 'angular-progress-http';

import { Query } from '../models/query';
import { SharedService } from '../services/shared';
import { RequestHelper } from '../helpers/request';
import { environment } from '../../environments/environment';

import * as urljoin from 'url-join';

import 'rxjs/add/operator/catch';

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

  getGeojsonsByRegion(regionId: string, query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
        this._http,
        'GET',
        urljoin(this._serverUrl, 'geojsons/region', regionId),
        query,
        progressListener
      );
  
      return request
        .map(res => res.json())
        .catch(this.handleError)
  }

  getGeojsonByTypeAndRegion(type: string, regionId: string, query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(
        this._http,
        'GET',
        urljoin(this._serverUrl, 'geojsons/type', type, 'region', regionId),
        query,
        progressListener
      );
  
      return request
        .map(res => res.json())
        .catch(this.handleError)
  }

  getSummariesByRegion(regionId: string, query: Query, progressListener: any): Observable<any> {
     let request = RequestHelper.generateHttpRequest(this._http, 
        'GET', 
        urljoin(this._serverUrl, 'summaries/region', regionId),
        query,
        progressListener
      );

      return request.map(res => res.json()).catch(this.handleError);
  }

  getSummariesExceptId(regionId: string, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(this._http, 
      'GET', 
      urljoin(this._serverUrl, 'summaries/get_except_id', regionId),
      {},
      progressListener
    );

    return request.map(res => res.json()).catch(this.handleError);
  }
  
  getRegionAvailableMaps( query: Query, progressListener: any): Observable<any> {
    let request = RequestHelper.generateHttpRequest(this._http, 
      'GET', 
      urljoin(this._serverUrl, 'summaries/region_available_maps'),
      query,
      progressListener
    );

    return request.map(res => res.json()).catch(this.handleError);
  }

  getSummaries(query: Query, progressListener: any): Observable<any> {
      let request = RequestHelper.generateHttpRequest(this._http, 
          'GET', 
          urljoin(this._serverUrl, 'summaries'),
          query,
          progressListener
      );

      return request.map(res => res.json()).catch(this.handleError);
  }

  getPenduduksByRegion(regionId: string, query: Query, progressListener: any): Observable<any> {
     let request = RequestHelper.generateHttpRequest(this._http, 
        'GET', 
        urljoin(this._serverUrl, 'penduduks/region', regionId),
        query,
        progressListener
      );

      return request.map(res => res.json()).catch(this.handleError);
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