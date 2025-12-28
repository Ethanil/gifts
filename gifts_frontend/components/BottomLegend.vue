<template>
    <!-- <v-bottom-sheet inset max-height="90%">
        <template #activator="{ props }">
            <v-btn icon="mdi-help" v-bind="props" />
        </template>
        <BottomLegendCard></BottomLegendCard>
    </v-bottom-sheet> -->
    <v-btn
        icon="mdi-help"
        :to="{ path: '/', query: {} }"
        :active="route.path == '/' && !route.query.giftlistname"
    />
</template>
<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>
