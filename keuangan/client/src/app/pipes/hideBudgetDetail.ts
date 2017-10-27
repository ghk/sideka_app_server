import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: 'hideBudgetDetail',
    pure: true
})
export class HideBudgetDetailPipe implements PipeTransform {
    private cachedData: any = null;

    transform(items: any[], filter: Object): any {        
        if (!items || items.length == 0 || !filter) {
            return items;
        }
        if (!this.cachedData) {
            let results = items.filter(item =>
                !item.harga_satuan && !item.harga_satuan_pak &&
                ((item.kode_rekening && item.kode_rekening.startsWith("4") && item.kode_rekening.split(".").length <= 3)
                    || !item.kode_rekening || item.kode_rekening == "5"
                    || (item.kode_rekening && item.kode_rekening.startsWith("6") && item.kode_rekening.split(".").length <= 3))
            );
            this.cachedData = results;
        }
        return this.cachedData;
    }
}

