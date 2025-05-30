// import this after install `@mdi/font` package
import "@mdi/font/css/materialdesignicons.css";
import { mdi } from "vuetify/iconsets/mdi";
import { customSVGs } from "~/assets/customSvgs";

import "vuetify/styles";
import { createVuetify } from "vuetify";

import { VDateInput } from "vuetify/labs/VDateInput";

export default defineNuxtPlugin((app) => {
    const vuetify = createVuetify({
        icons: {
            defaultSet: "mdi",
            sets: {
                mdi,
                custom: customSVGs,
            },
        },
        components: {
            VDateInput,
        },
    });
    app.vueApp.use(vuetify);
});
