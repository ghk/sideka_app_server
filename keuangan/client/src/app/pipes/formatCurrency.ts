import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: 'formatCurrency',
    pure: true
})
export class FormatCurrencyPipe implements PipeTransform {
    transform(item: number, fractionSize: number): any {
        if (isNaN(item))
            return item;
        if (item === 0)
            return "0";

        if (!fractionSize || fractionSize < 0)
            fractionSize = 1;

        let abs = Math.abs(item);
        let rounder = Math.pow(10, fractionSize);
        let isNegative = item < 0;
        let key = '';
        let powers = [
            { key: "Quantiliun", value: Math.pow(10, 15) },
            { key: "Trilyun", value: Math.pow(10, 12) },
            { key: "Milyar", value: Math.pow(10, 9) },
            { key: "Juta", value: Math.pow(10, 6) },
            { key: "Ribu", value: 1000 }
        ];

        for (let i = 0; i < powers.length; i++) {
            let reduced = abs / powers[i].value;
            reduced = Math.round(reduced * rounder) / rounder;
            if (reduced >= 1) {
                abs = reduced;
                key = powers[i].key;
                break;
            }
        }

        return (isNegative ? '-' : '') + abs + ' ' + key;
    }
}