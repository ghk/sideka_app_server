import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { NgModule, LOCALE_ID } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ProgressHttpModule } from 'angular-progress-http';
import { ChartsModule } from 'ng2-charts/ng2-charts';

import { AppComponent } from './components/app';
import { HeaderComponent } from './components/header';
import { ProgressComponent } from './components/progress';
import { ProgressRecapitulationComponent, FormatCurrencyPipe } from './components/progress-recapitulation';
import { ProgressTimelineComponent } from './components/progress-timeline';
import { ProgressDetailComponent } from './components/progress-detail';
import { SpendingComponent } from './components/spending';
import { SpendingRecapitulationComponent } from './components/spending-recapitulation';
import { SpendingDetailComponent, HideBudgetDetailPipe, BudgetTypePipe } from './components/spending-detail';
import { SpendingChartComponent } from './components/spending-chart';

import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    ProgressComponent,
    ProgressRecapitulationComponent,
    ProgressTimelineComponent,
    ProgressDetailComponent,
    SpendingComponent,
    SpendingRecapitulationComponent,
    SpendingDetailComponent,
    SpendingChartComponent,
    HideBudgetDetailPipe,
    BudgetTypePipe,
    FormatCurrencyPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpModule,
    ProgressHttpModule,
    ChartsModule,
    RouterModule.forRoot([
      { path: '', redirectTo: 'progress/region/0', pathMatch: 'full' },
      { path: 'progress/region/:regionId', component: ProgressComponent }, 
      { path: 'spending/region/:regionId', component: SpendingComponent },
      { path: '**', redirectTo: 'progress/region/0' }
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
