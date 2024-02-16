<template>
    <v-card>
        <div class="d-flex flex-row">
            <v-navigation-drawer>
                <v-tabs v-model="currentTab" direction="vertical">
                    <template v-for="(group, key) in giftgroups" :key="key">
                        <v-tab :value="key">
                            <v-badge
                                v-model="group.isInvited"
                                offset-x="-10"
                                color="primary"
                                icon="mdi-account-multiple-plus"
                            >
                                {{ group.name }}
                            </v-badge>
                        </v-tab>
                    </template>
                </v-tabs>
                <group-form
                    v-model:group-dialog="addGroupDialog"
                    :prop-group-data="groupDataToAdd"
                    @submit-form="addGroup"
                >
                    <template #activator="{ props }">
                        <v-btn v-bind="props" color="primary">
                            Weitere Liste hinzufügen
                        </v-btn>
                    </template>
                </group-form>
            </v-navigation-drawer>
            <v-skeleton-loader
                :loading="!currentGroup"
                type="heading, table"
                style="width: 100%"
            >
                <div style="width: 100%">
                    <v-banner
                        v-if="currentGroup!.isInvited"
                        width="75%"
                        icon="mdi-account-multiple-plus"
                        lines="one"
                        color="primary"
                        class="mx-auto my-4"
                        sticky
                        :elevation="12"
                    >
                        <v-banner-text>
                            Du wurdest eingeladen in dieser Gruppe beschenkt zu
                            werden!
                        </v-banner-text>

                        <template #actions>
                            <v-btn @click.stop="joinGroup">
                                Einladung annehmen
                            </v-btn>
                        </template>
                    </v-banner>
                    <v-card class="ma-auto py-7" min-width="90%" width="90%">
                        <v-card-title v-if="giftgroups[currentTab]">
                            <span
                                class="cursor-pointer"
                                @click.stop="editGroup(giftgroups[currentTab])"
                            >
                                {{ giftgroups[currentTab].name }}
                                <v-icon
                                    v-if="
                                        giftgroups[currentTab].editable &&
                                        giftgroups[currentTab].isBeingGifted
                                    "
                                    icon="mdi-pencil"
                                    size="small"
                                    @click.stop="
                                        editGroup(giftgroups[currentTab])
                                    "
                                />
                                <v-icon
                                    v-else
                                    icon="mdi-information"
                                    size="small"
                                    @click.stop="
                                        editGroup(giftgroups[currentTab])
                                    "
                                />
                            </span>
                        </v-card-title>
                        <v-data-table
                            :class="{ 'ma-4': true }"
                            :headers="tableHeaders"
                            :items="giftStore?.getGiftsOfCurrentGroup"
                            :sort-by="[{ key: 'giftStrength', order: 'desc' }]"
                            items-per-page="-1"
                        >
                            <template #[`item.picture`]="{ item }">
                                <v-avatar
                                    :image="item.picture as string"
                                    :size="60"
                                    @click="
                                        openPictureDialog(
                                            item.picture as string,
                                        )
                                    "
                                />
                            </template>
                            <template #[`item.giftStrength`]="{ item }">
                                <v-rating
                                    v-model="item.giftStrength"
                                    color="primary"
                                    :disabled="true"
                                    density="compact"
                                    size="small"
                                />
                            </template>
                            <template #[`item.price`]="{ item }">
                                {{ item.price }} €
                            </template>
                            <template #[`item.availableActions`]="{ item }">
                                <v-container>
                                    <v-row no-gutters>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'edit',
                                                )
                                            "
                                            text="Geschenk bearbeiten"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="editGift(item)"
                                                    >
                                                        mdi-pencil
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'delete',
                                                )
                                            "
                                            text="Geschenk löschen"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            openDeleteConfirmationDialog(
                                                                item,
                                                            )
                                                        "
                                                    >
                                                        mdi-delete
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'reserve',
                                                )
                                            "
                                            text="Geschenk reservieren"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                reserve: true,
                                                            })
                                                        "
                                                    >
                                                        mdi-lock
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'stop reserve',
                                                )
                                            "
                                            text="Reservierung löschen"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                reserve: false,
                                                            })
                                                        "
                                                    >
                                                        mdi-lock-off
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'free reserve',
                                                )
                                            "
                                            text="Zur Reservierung freigeben"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                freeReserve: true,
                                                            })
                                                        "
                                                    >
                                                        mdi-share
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'stop free reserve',
                                                )
                                            "
                                            text="Nicht mehr zur Reservierung freigeben"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                freeReserve: false,
                                                            })
                                                        "
                                                    >
                                                        mdi-share-off
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'request free reserve',
                                                )
                                            "
                                            text="Reservierungs freigabe erbitten"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                requestFreeReserve: true,
                                                            })
                                                        "
                                                    >
                                                        mdi-back-right
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip
                                            v-if="
                                                item.availableActions.includes(
                                                    'stop request free reserve',
                                                )
                                            "
                                            text="Nicht mehr Reservierungs freigabe erbitten"
                                            location="bottom"
                                        >
                                            <template #activator="{ props }">
                                                <v-col>
                                                    <v-icon
                                                        v-bind="props"
                                                        size="large"
                                                        @click="
                                                            do_Action(item, {
                                                                requestFreeReserve: false,
                                                            })
                                                        "
                                                    >
                                                        mdi-back-right-off
                                                    </v-icon>
                                                </v-col>
                                            </template>
                                        </v-tooltip>
                                    </v-row>
                                </v-container>
                            </template>
                            <template #bottom />
                        </v-data-table>
                        <gift-form
                            v-model:gift-dialog="addGiftDialog"
                            :prop-gift-data="giftDataToAdd"
                            @submit-form="addGift"
                        >
                            <template #activator="{ props }">
                                <v-btn color="primary" v-bind="props">
                                    {{ giftAddButtonText }}
                                </v-btn>
                            </template>
                        </gift-form>
                    </v-card>
                </div>
            </v-skeleton-loader>
        </div>
        <gift-form
            v-model:gift-dialog="editGiftDialog"
            v-model:gift-data="giftDataToEdit"
            :prop-gift-data="giftDataToEdit"
            submit-text="Bearbeitung speichern"
            @submit-form="updateGift"
        />
        <group-form
            v-model:group-dialog="editGroupDialog"
            :prop-group-data="groupDataToEdit"
            :new-group="false"
            @submit-form="updateGroup"
            @join-group="joinGroup"
        />
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
        <v-dialog v-model="pictureDialog" width="50%" height="75%">
            <v-img :src="curPicture" @click="pictureDialog = false" />
        </v-dialog>
    </v-card>
</template>
<script setup lang="ts">
//---------------- Table ----------------//
const giftgroupStore = useGiftGroupStore();
const giftStore = useGiftStore();
const currentTab = ref(0);
const currentGroup = computed(() => {
    if (giftgroups.value !== undefined && currentTab.value !== undefined)
        return giftgroups.value[currentTab.value];
    else return undefined;
});
onMounted(() => {
    giftgroupStore.loadFromAPI().then(() => {
        giftStore.loadFromAPI();
        giftStore.setGroup(giftgroupStore.giftgroups[0].id);
    });
});
watch(currentTab, async (newValue) => {
    await giftStore.setGroup(giftgroupStore.giftgroups[newValue].id);
});
const giftgroups = computed(() => {
    return giftgroupStore.$state.giftgroups;
});

const tableHeaders = [
    { title: "Bild", value: "picture", width: "10%" },
    { title: "Name", key: "name" },
    { title: "Beschreibung", value: "description" },
    { title: "Link", value: "link" },
    { title: "Preis", key: "price" },
    { title: "Wunschstärke", key: "giftStrength", width: "10%" },
    { title: "Aktionen", value: "availableActions", width: "165px" },
];

const pictureDialog = ref(false);
const curPicture = ref("");
function openPictureDialog(picture: string) {
    pictureDialog.value = true;
    curPicture.value = picture;
}

//**********************************************************************//
//-------------------------------- Gift --------------------------------//
//**********************************************************************//
//---------------- Add Gift ----------------//
const giftAddButtonText = computed(() => {
    if (
        !giftgroups.value ||
        giftgroups.value.length === 0 ||
        giftgroups.value[currentTab.value].isBeingGifted
    )
        return "Geschenk Hinzufügen";
    else return "Geschenk geheim vorschlagen";
});
const addGiftDialog = ref(false);
const giftDataToAdd = ref<Gift>({
    id: 0,
    name: "",
    price: 0,
    giftStrength: 3,
    description: "",
    link: "",
    picture: "",
    availableActions: [],
});
async function addGift(gift: Gift) {
    await giftStore.addGift(gift);
    addGiftDialog.value = false;
}

//---------------- Edit Gift ----------------//
const editGiftDialog = ref(false);
const giftDataToEdit = ref<Gift>({} as Gift);
async function updateGift(gift: Gift) {
    giftDataToEdit.value = gift;
    await giftStore.updateGift(gift);
    editGiftDialog.value = false;
}
function editGift(gift: Gift) {
    giftDataToEdit.value = gift;
    editGiftDialog.value = true;
}

//---------------- Delete Gift ----------------//
const deleteConfirmationDialog = ref(false);
const giftToDelete = ref<Gift>({} as Gift);
function openDeleteConfirmationDialog(gift: Gift) {
    giftToDelete.value = gift;
    deleteConfirmationDialog.value = true;
}
async function deleteGift() {
    giftStore.deleteGift(giftToDelete.value);
    deleteConfirmationDialog.value = false;
}

//---------------- Reserve, Free Reserve, Request Free Reserve Gift ----------------//
function do_Action(
    gift: Gift,
    queryParams: {
        reserve?: boolean;
        freeReserve?: boolean;
        requestFreeReserve?: boolean;
    },
) {
    giftStore.doAction(gift, queryParams);
}

//***********************************************************************//
//-------------------------------- Group --------------------------------//
//***********************************************************************//

//---------------- Add Group ----------------//
const addGroupDialog = ref(false);
const groupDataToAdd = ref<Giftgroup>({
    id: -1,
    editable: false,
    isBeingGifted: false,
    name: "",
    invitations: [],
});
async function addGroup(group: Giftgroup) {
    await giftgroupStore.addGroup(group);
    addGroupDialog.value = false;
}

//---------------- Edit Group ----------------//
const editGroupDialog = ref(false);
const groupDataToEdit = ref<Giftgroup>({
    id: -1,
    editable: false,
    isBeingGifted: false,
    name: "",
    invitations: [],
    invitableUser: [],
    usersBeingGifted: [],
} as Giftgroup);
function updateGroup(giftgroup: Giftgroup) {
    giftgroupStore.updateGroup(giftgroup).then(() => {
        currentTab.value = giftgroups.value.findIndex(
            (group) => group.id === giftgroup.id,
        );
        if (currentTab.value === -1) currentTab.value = 0;
        groupDataToEdit.value = giftgroups.value[currentTab.value];
        editGroupDialog.value = false;
    });
}
function editGroup(giftgroup: Giftgroup) {
    groupDataToEdit.value = giftgroup;
    editGroupDialog.value = true;
}

//---------------- Join Group ----------------//
function joinGroup() {
    const giftgroup = giftgroups.value[currentTab.value];
    giftgroupStore.joinGroup(giftgroup).then(() => {
        currentTab.value = giftgroups.value.findIndex(
            (group) => group.id === giftgroup.id,
        );
        groupDataToEdit.value = giftgroups.value[currentTab.value];
    });
}
</script>
