export default function (value: number) {
    return (input: string): boolean | string => {
        if (input.length<=value) return true;
        return `Limit von ${value} überschritten`;
    };
}
