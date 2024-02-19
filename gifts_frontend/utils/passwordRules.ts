export default [
    (password: string): boolean | string => {
        if (password.length >= 8) return true;
        return "Das Passwort muss mindestens 8 Zeichen lang sein";
    },
    (password: string): boolean | string => {
        if (password.match(/\d/) !== null) return true;
        return "Das Passwort muss mindestens 1 Zahl enthalten";
    },
    (password: string): boolean | string => {
        if (password.match(/[a-z]/) !== null) return true;
        return "Passwort muss mindestens 1 Kleinbuchstaben enthalten";
    },
    (password: string): boolean | string => {
        if (password.match(/[A-Z]/) !== null) return true;
        return "Passwort muss mindestens 1 Großbuchstaben enthalten";
    },
    (password: string): boolean | string => {
        if (password.match(/[^A-Za-z0-9]/) !== null) return true;
        return "Passwort muss mindestens 1 Sonderzeichen enthalten";
    },
];
