export default function (value: string) {
    return (input: string): boolean | string => {
        if (!isNaN(+input)) return true;
        return value + " muss eine Zahl sein";
    };
}
