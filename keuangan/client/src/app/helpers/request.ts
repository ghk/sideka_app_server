import { Http, RequestOptions, URLSearchParams, Response } from '@angular/http';
import { Observable } from 'rxjs'; 
import { ProgressHttp } from 'angular-progress-http';
import { Query } from '../models/query';

export class RequestHelper {

    constructor() { }

    static generateRequestOptions(query: Query) {
        let result = new RequestOptions();        
        if (!query)
            return result;

        let params = new URLSearchParams();
        if (query.page && query.perPage) {
            params.append('page', query.page.toString());
            params.append('per_page', query.perPage.toString());
        }
        if (query.sort)
            params.append('sort', query.sort);
        if (query.keywords)
            params.append('keywords', query.keywords);        
        result.params = params;
        
        return result;
    }

    static generateHttpRequest(http: ProgressHttp, method, url, query, downloadListener?, uploadListener?): Observable<Response> {        
        let options = this.generateRequestOptions(query);
        let req: any = http;
        options.method = method;

        if (downloadListener)
            req = req.withDownloadProgressListener(downloadListener);
        if (uploadListener)
            req = http.withUploadProgressListener(uploadListener);
        
        return req.request(url, options);
    }
}