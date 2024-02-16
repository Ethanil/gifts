<template>
    <v-banner
        :width="xlAndUp ? '75%' : '100%'"
        icon="mdi-comment-question-outline"
        :lines="xlAndUp ? 'one' : 'three'"
        color="primary"
        :class="{ 'mx-auto': true, 'my-4': true }"
        mobile-breakpoint="xl"
        :density="xlAndUp ? 'default' : 'compact'"
        sticky
        :elevation="12"
    >
        <v-banner-text>
            {{ bannerText }}
        </v-banner-text>
        <template #actions>
            <slot name="actions"> </slot>
        </template>
    </v-banner>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { xlAndUp } = useDisplay();
const _ = defineProps({
    bannerText: { type: String, required: true },
});
</script>
