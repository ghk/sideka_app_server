import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: 'regionType',
    pure: true
})
export class RegionTypePipe implements PipeTransform {

    transform(item: any, type: number): any {
        if (!item || !type) {
            return item;
        }
        return this.search(item, type);
    }

    search(item: any, type: number) {
        if (item.type === type)
            return item.name;    
        if (item.parent)
            return this.search(item.parent, type);     
        return '';
    }
}