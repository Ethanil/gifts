<template>
    <v-container class="mb-3">
        <v-row no-gutters>
            <template v-for="(action, key) in filteredActions" :key="key">
                <v-tooltip :text="action.tooltipText" location="bottom">
                    <template #activator="{ props }">
                        <v-col>
                            <v-icon
                                v-bind="props"
                                size="large"
                                :icon="action.icon"
                                @click="action.signal()"
                            >
                            </v-icon>
                        </v-col>
                    </template>
                </v-tooltip>
            </template>
        </v-row>
        <v-dialog v-model="deleteConfirmationDialog" max-width="450px">
            <v-card>
                <v-card-title>Löschen bestätigen</v-card-title>
                <v-card-text>
                    Sicher, dass du das Geschenk
                    <v-chip>{{ giftToDelete?.name }}</v-chip> löschen möchtest?
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="deleteGift">
                        Löschen bestätigen
                    </v-btn>
                    <v-btn
                        color="primary"
                        @click="deleteConfirmationDialog = false"
                    >
                        Abbrechen
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>
<script setup lang="ts">
import type { PropType } from "vue";

const outerProps = defineProps({
    item: { type: Object as PropType<Gift>, required: true },
});
const emits = defineEmits(["doAction", "edit", "delete"]);
const actions = [
    {
        actionType: "edit",
        tooltipText: "Geschenk bearbeiten",
        signal: () => emits("edit"),
        icon: "mdi-pencil",
    },
    {
        actionType: "delete",
        tooltipText: "Geschenk löschen",
        signal: () => openDeleteConfirmationDialog(),
        icon: "mdi-delete",
    },
    {
        actionType: "reserve",
        tooltipText: "Geschenk reservieren",
        signal: () => emits("doAction", outerProps.item, { reserve: true }),
        icon: "mdi-lock",
    },
    {
        actionType: "stop reserve",
        tooltipText: "Reservierung löschen",
        signal: () => emits("doAction", outerProps.item, { reserve: false }),
        icon: "mdi-lock-off",
    },
    {
        actionType: "free reserve",
        tooltipText: "Zur Reservierung freigeben",
        signal: () => emits("doAction", outerProps.item, { freeReserve: true }),
        icon: "mdi-share",
    },
    {
        actionType: "stop free reserve",
        tooltipText: "Nicht mehr zur Reservierung freigeben",
        signal: () =>
            emits("doAction", outerProps.item, { freeReserve: false }),
        icon: "mdi-share-off",
    },
    {
        actionType: "request free reserve",
        tooltipText: "Reservierungs freigabe erbitten",
        signal: () =>
            emits("doAction", outerProps.item, { requestFreeReserve: true }),
        icon: "custom:MessageLockOutline",
    },
    {
        actionType: "stop request free reserve",
        tooltipText: "Nicht mehr Reservierungs freigabe erbitten",
        signal: () =>
            emits("doAction", outerProps.item, { requestFreeReserve: false }),
        icon: "custom:MessageLockOffOutline",
    },
] as {
    actionType: string;
    tooltipText: string;
    signal: () => void;
    icon: string;
}[];
const filteredActions = computed(() =>
    actions.filter((action) =>
        outerProps.item.availableActions.includes(action.actionType),
    ),
);

//---------------- Delete Gift ----------------//
const deleteConfirmationDialog = ref(false);
const giftToDelete = ref<Gift>({} as Gift);
function openDeleteConfirmationDialog() {
    giftToDelete.value = outerProps.item;
    deleteConfirmationDialog.value = true;
}
async function deleteGift() {
    emits("delete");
    deleteConfirmationDialog.value = false;
}
</script>
