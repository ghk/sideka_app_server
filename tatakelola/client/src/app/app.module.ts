import { NgModule, LOCALE_ID } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { HttpModule } from '@angular/http';
import { ProgressHttpModule } from 'angular-progress-http';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';

import { AppComponent } from './components/app';
import { MapComponent } from './components/map';
import { DesaComponent } from './components/desa';
import { SearchComponent } from './components/search';
import { SidebarComponent } from './components/sidebar';
import { SummaryComponent } from './components/summary';
import { DataService } from './services/data';
import { SharedService } from './services/shared';

@NgModule({
  declarations: [
    AppComponent,
    MapComponent,
    DesaComponent,
    SearchComponent,
    SidebarComponent,
    SummaryComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpModule,
    ProgressHttpModule,
    LeafletModule.forRoot(),
    RouterModule.forRoot([
      { path: '', redirectTo: 'summary/region/0', pathMatch: 'full' },
      { path: 'summary/region/:regionId', component: SummaryComponent },
      { path: 'map', component: MapComponent },
      { path: 'desa/region/:regionId', component: DesaComponent }
    ])
  ],
  providers: [
    DataService,
    SharedService,
    { provide: LOCALE_ID, useValue: 'id-ID' }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
