export default function (value: string) {
    return (input: string): boolean | string => {
        if (input) return true;
        return value + " eingeben";
    };
}