import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { NgModule, LOCALE_ID } from '@angular/core';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';

import { AppComponent } from './components/app';
import { MapComponent } from './components/map';
import { SearchComponent } from './components/search';
import { SidebarComponent } from './components/sidebar';

@NgModule({
  declarations: [
    AppComponent,
    MapComponent,
    SearchComponent,
    SidebarComponent
  ],
  imports: [    
    BrowserModule,
    BrowserAnimationsModule,    
    LeafletModule.forRoot(),    
    RouterModule.forRoot([
      { path: '', redirectTo: 'map', pathMatch: 'full' },
      { path: 'map', component: MapComponent }
    ])
  ],
  providers: [
    { provide: LOCALE_ID, useValue: 'id-ID' }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
