<template>
    <NuxtLayout>
        <v-app>
            <v-system-bar v-if="false" />
            <v-main>
                <NuxtPage />
            </v-main>
        </v-app>
    </NuxtLayout>
</template>

<script lang="ts" setup>
import { useTheme } from "vuetify";

const theme = useTheme();
onMounted(() => {
    const selectedTheme = localStorage.getItem("selectedTheme");
    if (selectedTheme) {
        theme.global.name.value = selectedTheme;
    } else {
        localStorage.setItem("selectedTheme", "light");
    }
});
</script>
