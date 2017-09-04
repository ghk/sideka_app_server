import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ProgressHttpModule } from 'angular-progress-http';

import { AppComponent } from './components/app';
import { HeaderComponent } from './components/header';
import { ProgressRecapitulationComponent } from './components/progress-recapitulation';

import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    ProgressRecapitulationComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpModule,
    ProgressHttpModule,
    RouterModule.forRoot([
      { path: '', redirectTo: '', pathMatch: 'full' },
      { path: 'progress', component: ProgressRecapitulationComponent}
    ]),
  ],
  providers: [
    DataService,
    SharedService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
