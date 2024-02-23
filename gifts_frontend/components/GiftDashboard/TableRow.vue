<template>
    <tr v-if="lgAndUp" class="v-data-table__tr">
        <template
            v-for="([key, val], index) in Object.entries(internalItem.columns)"
            :key="index"
        >
            <GiftDashboardTableCell
                :item="item"
                :item-key="key"
                :item-val="val"
                @delete-gift="deleteGift"
                @do-action="doAction"
                @edit-gift="editGift"
                @open-picture-dialog="
                    emit('openPictureDialog', item.picture as string)
                "
            />
        </template>
    </tr>
    <template v-else>
        <GiftDashboardTableCell
            :item="item"
            item-key=""
            item-val=""
            mobile
            @delete-gift="deleteGift"
            @do-action="doAction"
            @edit-gift="editGift"
            @open-picture-dialog="
                emit('openPictureDialog', item.picture as string)
            "
        />
    </template>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();

import type { PropType } from "vue";
const outerProps = defineProps({
    item: { type: Object as PropType<Gift>, required: true },
    internalItem: { type: Object, required: true },
    headers: {
        type: Array<any>,
        required: true,
    },
});
const emit = defineEmits([
    "doAction",
    "editGift",
    "deleteGift",
    "openPictureDialog",
]);
function doAction(queryParams: any) {
    emit("doAction", outerProps.item, queryParams);
}
function editGift() {
    emit("editGift", outerProps.item);
}
function deleteGift() {
    emit("deleteGift", outerProps.item);
}
</script>
