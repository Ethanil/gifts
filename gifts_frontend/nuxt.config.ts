import vuetify, { transformAssetUrls } from "vite-plugin-vuetify";
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    app: {
        head: {
            link: [{ rel: "icon", type: "image/svg", href: "/favicon.svgg" }],
        },
    },
    ssr: false,
    modules: [
        "@pinia/nuxt",
        "@sidebase/nuxt-auth",
        ["@nuxtjs/eslint-module", { lintOnStart: false }],
        (_options, nuxt) => {
            nuxt.hooks.hook("vite:extendConfig", (config) => {
                // @ts-expect-error
                config.plugins.push(vuetify({ autoImport: true }));
            });
        },
    ],
    build: {
        transpile: ["vuetify"],
    },
    vite: {
        vue: {
            template: {
                transformAssetUrls,
            },
        },
    },
    auth: {
        baseURL: process.env.NODE_ENV !== 'production' ? "http://127.0.0.1:5000/api" : `https://${process.env.EXPOSED_BACKEND_URL}`,
        provider: {
            type: "local",
            endpoints: {
                signIn: { path: "/auth/login", method: "post" },
                signOut: { path: "", method: "" },
                signUp: { path: "/users", method: "post" },
                getSession: { path: "/auth/getSession", method: "get" },
            },
            pages: {
                login: "/login",
            },
            token: {
                signInResponseTokenPointer: "/access_token",
                maxAgeInSeconds: 60 * 60 * 24 * 3,
            },
        },
        globalAppMiddleware: true,
    },
});
