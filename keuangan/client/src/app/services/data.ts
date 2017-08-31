import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import 'rxjs/add/observable/of';

@Injectable()
export class DataService {

  constructor() { }

  getTransferBundle(): Observable<any> { 
    return Observable.of(null);
  }

}