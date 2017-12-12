import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: 'budgetType',
    pure: true
})
export class BudgetTypePipe implements PipeTransform {
    transform(items: any[], type: Object): any {
        if (!items || items.length == 0 || !type) {
            return items;
        }
        let results = items.filter(item => (type === '5' && !item.kode_rekening) || (item.kode_rekening && item.kode_rekening.startsWith(type)));
        return results;
    }
}