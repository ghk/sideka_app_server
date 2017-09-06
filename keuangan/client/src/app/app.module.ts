import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { NgModule, LOCALE_ID } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ProgressHttpModule } from 'angular-progress-http';
import { ChartsModule } from 'ng2-charts/ng2-charts';

import { AppComponent } from './components/app';
import { HeaderComponent } from './components/header';
import { ProgressRecapitulationComponent } from './components/progress-recapitulation';
import { ProgressTimelineComponent } from './components/progress-timeline';
import { SpendingRecapitulationComponent } from './components/spending-recapitulation';

import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    ProgressRecapitulationComponent,
    ProgressTimelineComponent,
    SpendingRecapitulationComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpModule,
    ProgressHttpModule,
    ChartsModule,
    RouterModule.forRoot([
      { path: '', redirectTo: '', pathMatch: 'full' },
      { path: 'progress', component: ProgressRecapitulationComponent }, 
      { path: 'realization', component: SpendingRecapitulationComponent }
    ]),
  ],
  providers: [
    DataService,
    SharedService,
    { provide: LOCALE_ID, useValue: 'id-ID' }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
