module.exports = {
    root: true,
    extends: ["@nuxt/eslint-config", "plugin:nuxt/recommended", "prettier"],
    rules: {
        "@typescript-eslint/no-unused-vars": [
            "error",
            {
                argsIgnorePattern: "^_",
                varsIgnorePattern: "^_",
            },
        ],
    },
};
