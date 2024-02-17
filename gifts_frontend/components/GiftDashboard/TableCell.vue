<template>
    <template v-if="itemKey == 'picture'">
        <v-img v-if="mobile" :src="item.picture as string" height="100px" />
        <v-avatar
            v-else
            :image="item.picture as string"
            :size="60"
            class="cursor-pointer"
            @click="emit('openPictureDialog')"
        />
    </template>
    <template v-else-if="itemKey == 'giftStrength'">
        <v-rating
            v-model="rating"
            color="primary"
            :disabled="true"
            density="compact"
            size="small"
        />
    </template>
    <template v-else-if="itemKey == 'price'"> {{ itemVal }} € </template>
    <template v-else-if="itemKey == 'availableActions'">
        <GiftDashboardActions
            :item="item"
            @do-action="(gift, queryParams) => emit('doAction', queryParams)"
            @edit="emit('editGift')"
            @delete="emit('deleteGift')"
        />
    </template>
    <template v-else-if="itemKey == 'name'">
        <v-tooltip v-if="item.isSecretGift" location="bottom">
            <template #activator="{ props }">
                <v-badge
                    icon="mdi-eye-off-outline"
                    offset-x="-12"
                    color="primary"
                    v-bind="props"
                >
                    {{ itemVal }}
                </v-badge>
            </template>
            Dies ist ein geheimes Geschenk
        </v-tooltip>
        <span v-else>{{ itemVal }}</span>
    </template>
    <template v-else-if="itemKey == 'link'"
        ><a :href="itemVal" target="_blank">{{ itemVal }}</a></template
    >
    <template v-else>{{ itemVal }}</template>
</template>
<script setup lang="ts">
import type { PropType } from "vue";
const outerProps = defineProps({
    itemKey: { type: String, required: true },
    itemVal: {
        type: [Object, String, Number] as PropType<any>,
        required: true,
    },
    item: { type: Object as PropType<Gift>, required: true },
    mobile: { type: Boolean, default: false },
});
const rating = outerProps.item.giftStrength;
const emit = defineEmits([
    "openPictureDialog",
    "doAction",
    "editGift",
    "deleteGift",
]);
</script>
