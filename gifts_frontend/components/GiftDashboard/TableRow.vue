<template>
    <tr v-if="lgAndUp" class="v-data-table__tr">
        <template
            v-for="([key, val], index) in Object.entries(internalItem.columns)"
            :key="index"
        >
            <td class="v-data-table__td v-data-table-column--align-start">
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
            </td>
        </template>
    </tr>
    <template v-else>
        <v-container>
            <v-row
                v-for="([key, val], index) in Object.entries(
                    internalItem.columns,
                )"
                :key="index"
                density="compact"
                slim
            >
                <v-col>
                    {{ headers[index].title }}
                </v-col>
                <v-col>
                    <GiftDashboardTableCell
                        :item="item"
                        :item-key="key"
                        :item-val="val"
                        mobile
                        @delete-gift="deleteGift"
                        @do-action="doAction"
                        @edit-gift="editGift"
                        @open-picture-dialog="
                            emit('openPictureDialog', item.picture as string)
                        "
                    />
                </v-col>
            </v-row>
            <v-divider />
        </v-container>
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
function doAction(gift: Gift, queryParams: any) {
    emit("doAction", outerProps.item, queryParams);
}
function editGift(gift: Gift) {
    emit("editGift", outerProps.item);
}
function deleteGift(gift: Gift) {
    emit("deleteGift", outerProps.item);
}
</script>
