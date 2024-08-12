<template>
    <NuxtLayout>
        <v-app>
            <v-system-bar v-if="false" />
            <v-main :style="'--v-layout-bottom:' +mobileButtonHeight +'px'">
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
const mobileButtonHeight = ref(0);
const updateMobileButtonHeight = () => {
    const mobileButton = document.querySelector("#mobileButton");
    if(mobileButton) {mobileButtonHeight.value = mobileButton.clientHeight;}
    else mobileButtonHeight.value = 0;
}
window.addEventListener("resize", updateMobileButtonHeight);
</script>
