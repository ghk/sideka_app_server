import { Component, OnInit, OnDestroy } from '@angular/core';
import { SharedService } from '../services/shared';

@Component({
  selector: 'sk-header',
  templateUrl: '../templates/header.html',
})

export class HeaderComponent implements OnInit, OnDestroy {

  state: any;
  region: any;

  constructor(
    private _sharedService: SharedService
  ) { }

  ngOnInit(): void { 
    this._sharedService.getRegion().subscribe(region => {
      this.region = region;
    });

    this._sharedService.getState().subscribe(state => {
      this.state = state;
    });
  }

  ngOnDestroy(): void { }
}
