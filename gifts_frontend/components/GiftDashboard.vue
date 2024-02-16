<template>
    <v-card>
        <div class="d-flex flex-row">
            <v-navigation-drawer v-model="navBarToggle">
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
                        <v-btn v-bind="props" color="primary" icon="mdi-plus" size="45">
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
                    <GiftDashboardBanner
                        v-if="currentGroup!.isInvited"
                        :banner-text="'Du wurdest eingeladen in dieser Gruppe beschenkt zu werden!'"
                    >
                        <template #actions>
                            <v-btn
                                text="Einladung annehmen"
                                @click.stop="joinGroup"
                            />
                        </template>
                    </GiftDashboardBanner>
                    <GiftDashboardBanner
                        v-for="(gift, key) in giftsWithFreeReserveRequest"
                        :key="key"
                        :banner-text="generateFreeReserveText(gift)"
                    >
                        <template #actions>
                            <v-btn
                                text="Annehmen"
                                @click.stop="
                                    do_Action(gift, {
                                        freeReserve: true,
                                    })
                                "
                            />
                            <v-btn
                                text="Ablehnen"
                                @click.stop="
                                    do_Action(gift, {
                                        denyFreeReserve: true,
                                    })
                                "
                            />
                        </template>
                    </GiftDashboardBanner>
                    <v-card class="ma-auto py-7" min-width="90%" width="90%">
                        <v-card-title v-if="giftgroups[currentTab]">
                            <v-row>
                                <v-col>
                                    <span
                                        class="cursor-pointer"
                                        @click.stop="
                                            editGroup(giftgroups[currentTab])
                                        "
                                    >
                                        {{ giftgroups[currentTab].name }}
                                        <v-icon
                                            v-if="
                                                giftgroups[currentTab]
                                                    .editable &&
                                                giftgroups[currentTab]
                                                    .isBeingGifted
                                            "
                                            icon="mdi-pencil"
                                            size="small"
                                            @click.stop="
                                                editGroup(
                                                    giftgroups[currentTab],
                                                )
                                            "
                                        />
                                        <v-icon
                                            v-else
                                            icon="mdi-information"
                                            size="small"
                                            @click.stop="
                                                editGroup(
                                                    giftgroups[currentTab],
                                                )
                                            "
                                        />
                                    </span>
                                </v-col>
                                <v-col>
                                    <gift-form
                                        v-model:gift-dialog="addGiftDialog"
                                        :prop-gift-data="giftDataToAdd"
                                        @submit-form="addGift"
                                    >
                                        <template #activator="{ props }">
                                            <v-btn
                                                color="primary"
                                                v-bind="props"
                                            >
                                                {{ giftAddButtonText }}
                                            </v-btn>
                                        </template>
                                    </gift-form>
                                </v-col>
                            </v-row>
                        </v-card-title>
                        <v-data-table
                            :class="{ 'ma-4': true }"
                            :headers="tableHeaders"
                            :items="giftStore?.getGiftsOfCurrentGroup"
                            :sort-by="[{ key: 'giftStrength', order: 'desc' }]"
                            items-per-page="-1"
                        >
                            <template v-if="!lgAndUp" #headers></template>
                            <template #item="{ index, internalItem, item }">
                                <GiftDashboardTableRow
                                    :item="item"
                                    :internal-item="internalItem"
                                    :headers="tableHeaders"
                                    @delete-gift="deleteGift"
                                    @edit-gift="editGift"
                                    @do-action="do_Action"
                                    @open-picture-dialog="openPictureDialog"
                                />
                            </template>
                            <template #bottom />
                        </v-data-table>
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
        <v-dialog v-model="pictureDialog" width="50%" height="75%">
            <v-img :src="curPicture" @click="pictureDialog = false" />
        </v-dialog>
    </v-card>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();
const outerProps = defineProps({ navBar: { type: Boolean, default: true } });
const navBarToggle = ref(outerProps.navBar);
watch(outerProps, (newValue) => (navBarToggle.value = newValue.navBar));
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
    { title: "Name", key: "name", value: "name" },
    { title: "Beschreibung", value: "description" },
    { title: "Link", value: "link" },
    { title: "Preis", key: "price", value: "price" },
    {
        title: "Wunschstärke",
        key: "giftStrength",
        value: "giftStrength",
        width: "10%",
    },
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
async function deleteGift(gift: Gift) {
    await giftStore.deleteGift(gift);
}

//---------------- Reserve, Free Reserve, Request Free Reserve Gift ----------------//
function generateFreeReserveText(gift: Gift) {
    if (!gift.freeForReservationRequest) return "";
    let result = gift.freeForReservationRequest.reduce(
        (previousValue, currentValue, currentIndex) =>
            `${previousValue}${currentValue.firstName} ${currentValue.lastName}
            ${
                currentIndex + 1 < gift.freeForReservationRequest!.length
                    ? currentIndex + 2 ===
                      gift.freeForReservationRequest!.length
                        ? " und "
                        : ", "
                    : " "
            }`,
        "",
    );
    result += `hat angefragt, ob du das Geschenk ${gift.name} zusammen schenken willst!`;
    return result;
}
function do_Action(
    gift: Gift,
    queryParams: {
        reserve?: boolean;
        freeReserve?: boolean;
        requestFreeReserve?: boolean;
        denyFreeReserve?: boolean;
    },
) {
    giftStore.doAction(gift, queryParams);
}
const giftsWithFreeReserveRequest = computed(() =>
    giftStore.getGiftsOfCurrentGroup.filter(
        (gift) =>
            gift.freeForReservationRequest &&
            gift.freeForReservationRequest.length > 0,
    ),
);
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
