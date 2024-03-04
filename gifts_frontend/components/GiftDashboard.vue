<template>
    <div class="d-flex flex-row">
        <v-navigation-drawer
            v-model="navBarToggle"
            @update:model-value="emits('navBarToggle')"
        >
            <v-checkbox v-model="groupAsUser" label="Group"></v-checkbox>
            <v-tabs
                v-if="!groupAsUser"
                v-model="currentTab"
                direction="vertical"
            >
                <template v-for="(group, key) in giftgroups" :key="key">
                    <v-tab :value="key">
                        <v-badge
                            v-model="group.isInvited"
                            offset-x="-10"
                            color="primary"
                            icon="mdi-account-multiple-plus"
                        >
                            <span class="tabtext">{{ group.name }}</span>
                        </v-badge>
                    </v-tab>
                </template>
            </v-tabs>
            <template v-else>
                <v-tabs v-model="currentTab" direction="vertical" :max="1">
                    <template
                        v-for="([outerKey, groupObject], i) in Object.entries(
                            giftgroupsPerUser,
                        )"
                        :key="i"
                    >
                        <v-tab
                            slim
                            hide-slider
                            :value="-1"
                            disabled
                            density="compact"
                        >
                            {{ outerKey }}
                        </v-tab>
                        <template
                            v-for="([key, group], j) in Object.entries(
                                groupObject,
                            )"
                            :key="j"
                        >
                            <v-tab
                                :class="
                                    currentTab.toString() === key
                                        ? 'v-slide-group-item--active v-tab--selected'
                                        : ''
                                "
                                :value="key"
                                density="compact"
                            >
                                <v-badge
                                    v-model="group.isInvited"
                                    offset-x="-10"
                                    color="primary"
                                    icon="mdi-account-multiple-plus"
                                >
                                    <span class="tabtext">
                                        {{ group.name }}
                                    </span>
                                </v-badge>
                            </v-tab>
                        </template>
                    </template>
                </v-tabs>
            </template>
            <v-tabs hide-slider direction="vertical">
                <v-tab disabled height="20px" />
                <v-tab
                    color="primary"
                    elevation="10"
                    append-icon="mdi-plus"
                    variant="outlined"
                    @click="addGroupDialog = true"
                >
                    Liste erstellen
                </v-tab>
            </v-tabs>
        </v-navigation-drawer>
        <v-skeleton-loader
            :loading="!currentGroup"
            type="heading, table"
            style="width: 100%"
        >
            <GiftDashboardBanner
                v-if="currentGroup!.isInvited"
                :banner-text="'Du wurdest eingeladen in dieser Gruppe beschenkt zu werden!'"
            >
                <template #actions>
                    <v-btn text="Annehmen" @click.stop="joinGroup" />
                    <v-btn text="Ablehnen" @click.stop="declineInvitation" />
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
            <div
                v-if="giftgroups[currentTab] && !currentGroup!.isInvited"
                class="ma-auto pa-7"
                style="width: 100%; height: 100%"
            >
                <v-container>
                    <v-row>
                        <v-col>
                            <span
                                class="text-h5 cursor-pointer"
                                @click.stop="editGroup(giftgroups[currentTab])"
                            >
                                {{ giftgroups[currentTab].name }}
                                <v-icon
                                    :icon="
                                        giftgroups[currentTab].editable &&
                                        (giftgroups[currentTab].isBeingGifted ||
                                            giftgroups[currentTab]
                                                .isSecretGroup)
                                            ? 'mdi-pencil'
                                            : 'mdi-information'
                                    "
                                    size="small"
                                    @click.stop="
                                        editGroup(giftgroups[currentTab])
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
                                        :class="'pa-4'"
                                        height="min-content"
                                        width="min-content"
                                        color="primary"
                                        id="AddButton"
                                        v-bind="props"
                                    >
                                        <template v-if="isOwnGroup" #prepend>
                                            <v-img
                                                width="80px"
                                                height="80px"
                                                :rounded="0"
                                                src="\assets\icons\normal_gift.png"
                                            ></v-img>
                                        </template>
                                        <template v-else #prepend>
                                            <v-img
                                                width="80px"
                                                height="80px"
                                                :rounded="0"
                                                src="\assets\icons\secret_gift.png"
                                            ></v-img>
                                        </template>
                                        <span
                                            style="
                                                white-space: break-spaces;
                                                font-size: 1.1em;
                                            "
                                            >{{ giftAddButtonText }}</span
                                        >
                                    </v-btn>
                                    <v-btn
                                        :class="
                                            !buttonCurrentlyIntersecting
                                                ? 'pa-4 floatingButton'
                                                : 'pa-4 floatingButton outOfView'
                                        "
                                        height="min-content"
                                        width="min-content"
                                        color="primary"
                                        v-bind="props"
                                    >
                                        <template v-if="isOwnGroup" #prepend>
                                            <v-img
                                                width="80px"
                                                height="80px"
                                                :rounded="0"
                                                src="\assets\icons\normal_gift.png"
                                            ></v-img>
                                        </template>
                                        <template v-else #prepend>
                                            <v-img
                                                width="80px"
                                                height="80px"
                                                :rounded="0"
                                                src="\assets\icons\secret_gift.png"
                                            ></v-img>
                                        </template>
                                        <span
                                            style="
                                                white-space: break-spaces;
                                                font-size: 1.1em;
                                            "
                                            >{{ giftAddButtonText }}</span
                                        >
                                    </v-btn>
                                </template>
                            </gift-form>
                        </v-col>
                    </v-row>
                </v-container>
                <v-data-table
                    :headers="tableHeaders"
                    :items="giftStore?.getGiftsOfCurrentGroup"
                    :sort-by="[{ key: 'giftStrength', order: 'desc' }]"
                    items-per-page="-1"
                >
                    <template v-if="!lgAndUp" #headers></template>
                    <template #item="{ internalItem, item }">
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
        :users-loaded="usersLoaded"
        :new-group="false"
        @submit-form="updateGroup"
        @join-group="joinGroup"
    />
    <group-form
        v-model:group-dialog="addGroupDialog"
        :prop-group-data="groupDataToAdd"
        :users-loaded="usersLoaded"
        @submit-form="addGroup"
    />
    <v-dialog v-model="pictureDialog" width="50%" height="75%">
        <v-img :src="curPicture" @click="pictureDialog = false" />
    </v-dialog>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();
const navBarToggle = defineModel<boolean>("navBarToggle", {
    type: Boolean,
    required: true,
});
const emits = defineEmits(["navBarToggle"]);
//---------------- Table ----------------//
const giftgroupStore = useGiftGroupStore();
const giftStore = useGiftStore();
const currentTab = ref(0);
const currentGroup = computed(() => {
    if (giftgroups.value !== undefined && currentTab.value !== undefined)
        return giftgroups.value[currentTab.value];
    else return undefined;
});
const buttonCurrentlyIntersecting = ref(true);
const userStore = useUserStore();
const usersLoaded = ref(false);
onMounted(() => {
    giftgroupStore.loadFromAPI().then(() => {
        giftStore.loadFromAPI();
        giftStore.setGroup(giftgroupStore.giftgroups[0].id);
    });
    userStore.loadFromAPI().then(() => (usersLoaded.value = true));
    let observer = new IntersectionObserver((e) => {
        buttonCurrentlyIntersecting.value = e[0].isIntersecting;
    });
    setTimeout(() => {
        const target = document.querySelector("#AddButton");
        if (target) observer.observe(target);
    }, 50);
});
watch(currentTab, async (newValue) => {
    await giftStore.setGroup(giftgroupStore.giftgroups[newValue].id);
});
const giftgroups = computed(() => {
    return giftgroupStore.giftgroups;
});

const groupAsUser = ref(false);
const giftgroupsPerUser = computed(() => {
    const result = {} as { [key: string]: { [key: number]: Giftgroup } };
    for (const [index, group] of giftgroups.value.entries()) {
        if (!group.usersBeingGifted) continue;
        for (const user of group.usersBeingGifted) {
            const fullname = `${user.firstName} ${user.lastName}`;
            if (!Object.hasOwn(result, fullname))
                result[fullname] = {} as { [key: number]: Giftgroup };
            result[fullname][index] = group;
        }
    }
    return result;
});

const tableHeaders = computed(() => {
    const res = [
        { title: "Bild", value: "picture", width: "100px", align: "center" },
        { title: "Name", key: "name", value: "name", width: "15%" },
        { title: "Beschreibung", value: "description" },
        { title: "Link", value: "link", width: "45px" },
        { title: "Preis", key: "price", value: "price", width: "100px" },
        {
            title: "Wunschstärke",
            key: "giftStrength",
            value: "giftStrength",
            width: "143px",
        },
        {
            title: "Aktionen",
            value: "availableActions",
            width: "165px",
            align: "center",
        },
    ] as any[];
    if (!currentGroup.value?.isBeingGifted)
        res.push({
            title: "Reserviert",
            key: "reservingUsers",
            value: "reservingUsers",
            width: "150px",
            align: "center",
        });
    return res;
});

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
const isOwnGroup = computed(
    () => !giftgroups.value || giftgroups.value[currentTab.value].isBeingGifted,
);
const giftAddButtonText = computed(() => {
    if (isOwnGroup.value) return "Geschenk Hinzufügen";
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
    isSecretGroup: false,
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
    isSecretGroup: false,
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
function declineInvitation() {
    const giftgroup = giftgroups.value[currentTab.value];
    giftgroupStore.declineInvitation(giftgroup).then(() => {
        currentTab.value = giftgroups.value.findIndex(
            (group) => group.id === giftgroup.id,
        );
        groupDataToEdit.value = giftgroups.value[currentTab.value];
    });
}
</script>
<style lang="scss">
.tabtext {
    text-transform: none;
    letter-spacing: normal;
}
.floatingButton {
    transition-duration: 0.7s;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    top: 0px;
    right: 0px;
    transform: translate(80%);
    position: fixed;
    z-index: 10;
    &:hover {
        transform: translate(1%);
    }
}
.outOfView {
    transform: translate(100%);
}
</style>
