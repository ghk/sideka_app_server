import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';

import { AppComponent } from './components/app';
import { HeaderComponent } from './components/header';
import { TransferRecapitulationComponent } from './components/transfer-recapitulation';

import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    TransferRecapitulationComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule.forRoot([
      { path: '', redirectTo: '', pathMatch: 'full' },
      { path: 'transfer', component: TransferRecapitulationComponent}
    ])
  ],
  providers: [
    DataService,
    SharedService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
