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
import { ProgressDetailComponent } from './components/progress-detail';
import { SpendingRecapitulationComponent } from './components/spending-recapitulation';
import { SpendingDetailComponent } from './components/spending-detail';

import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    ProgressRecapitulationComponent,
    ProgressTimelineComponent,
    ProgressDetailComponent,
    SpendingRecapitulationComponent,
    SpendingDetailComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpModule,
    ProgressHttpModule,
    ChartsModule,
    RouterModule.forRoot([
      { path: '', redirectTo: 'progress', pathMatch: 'full' },
      { path: 'progress', component: ProgressRecapitulationComponent }, 
      { path: 'progress/region/:regionId', component: ProgressDetailComponent },
      { path: 'spending', component: SpendingRecapitulationComponent },
      { path: 'spending/region/:regionId', component: SpendingDetailComponent }
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
