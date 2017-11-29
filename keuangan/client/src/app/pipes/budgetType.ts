import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: 'budgetType',
    pure: true
})
export class BudgetTypePipe implements PipeTransform {
    private type: string;
    private cache: any[];

    transform(items: any[], type: Object): any {
        if (!items || items.length == 0 || !type) {
            return items;
        }
        if (type !== this.type || !this.cache) {
            let results = items.filter(item => (type === '5' && !item.kode_rekening) || (item.kode_rekening && item.kode_rekening.startsWith(type)));
            this.type = type.toString();
            this.cache = results;            
        }
        return this.cache;
    }
}