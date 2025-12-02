<template>
    <v-dialog
        v-model="groupDialog"
        :max-width="showInviteCol ? '1200px' : '900px'"
    >
        <template #activator="{ props }">
            <slot name="activator" :props="props" />
        </template>
        <v-card>
            <v-skeleton-loader :loading="!usersLoaded">
                <div class="v-system-bar">
                    <v-icon @click="groupDialog = false"> mdi-close </v-icon>
                </div>
                <v-alert v-if="willDeleteGroup" type="error">
                    DIE LISTE WIRD GELÖSCHT
                </v-alert>
                <v-form
                    ref="form"
                    class="pa-5 pt-3"
                    style="width: 100%"
                    @submit.prevent="submitForm"
                >
                    <template v-if="isAllowedToEditTitle">
                        <v-text-field
                            v-model="groupData.name"
                            label="Name der Liste"
                            :counter="20"
                            :rules="[
                                nonEmptyRule('Name der Liste'),
                                maxCharRule(20),
                            ]"
                        />
                        <v-checkbox
                            v-if="newGroup"
                            v-model="groupData.isSecretGroup"
                            label="Geheime Gruppe"
                            validate-on="input"
                            :rules="[someoneIsBeingGiftedRule()]"
                        />
                    </template>
                    <v-card-title v-else class="d-flex justify-center">
                        {{ outerProps.propGroupData.name }}
                    </v-card-title>
                    <span v-if="groupData.isSecretGroup" class="text-subtitle1"
                        >Dies ist eine geheime Gruppe, die Beschenkten können
                        diese Gruppe nicht sehen! <br
                    /></span>
                    <div v-if="isOwner">
                        <v-container> </v-container>
                        <v-row v-if="groupData.shareToken">
                            <v-col>
                                <span>
                                    {{ shareLink }}
                                    <v-icon
                                        icon="mdi-content-copy"
                                        @click="copyShareLinkToClipboard"
                                    ></v-icon
                                ></span>
                            </v-col>
                        </v-row>
                        <v-row>
                            <v-col :cols="shareCols">
                                <v-date-input
                                    v-model="shareTokenDate"
                                    :allowed-dates="onlyFutureDates"
                                    label="Link gültig bis"
                                    :hide-details="true"
                                    :display-format="dateFormat"
                                ></v-date-input>
                            </v-col>
                            <v-col :cols="shareCols">
                                <v-btn
                                    :disabled="
                                        shareTokenDate === undefined ||
                                        isNaN(shareTokenDate.getTime())
                                    "
                                    color="primary"
                                    :style="shareButtonStyle"
                                    @click="generateShareToken"
                                >
                                    <span
                                        style="
                                            white-space: break-spaces;
                                            font-size: 1.1em;
                                        "
                                        >Teilbaren Link erzeugen</span
                                    >
                                </v-btn>
                            </v-col>
                            <v-col :cols="shareCols">
                                <v-btn
                                    :disabled="
                                        groupData.shareToken == '' ||
                                        shareTokenDate ==
                                            groupData.shareTokenExpireDate
                                    "
                                    color="primary"
                                    :style="shareButtonStyle"
                                    @click="changeShareTokenDate"
                                >
                                    <span
                                        style="
                                            white-space: break-spaces;
                                            font-size: 1.1em;
                                        "
                                        >Datum aktualisieren</span
                                    >
                                </v-btn>
                            </v-col>
                            <v-col :cols="shareCols">
                                <v-btn
                                    :disabled="groupData.shareToken == ''"
                                    color="primary"
                                    :style="shareButtonStyle"
                                    @click="deleteShareToken"
                                >
                                    <span
                                        style="
                                            white-space: break-spaces;
                                            font-size: 1.1em;
                                        "
                                        >Teilbaren Link löschen</span
                                    >
                                </v-btn>
                            </v-col>
                        </v-row>
                    </div>
                    <v-container>
                        <v-row no-gutters>
                            <v-col class="d-flex justify-center" :cols="cols">
                                <v-container>
                                    <v-row>
                                        <group-form-list
                                            :users="
                                                groupData.usersBeingGifted ?? []
                                            "
                                            :title="
                                                groupData.isSecretGroup
                                                    ? 'Geheim Beschenkte'
                                                    : 'Beschenkte'
                                            "
                                            title-icon="mdi-gift-open-outline"
                                            action-icon="mdi-delete-outline"
                                            :action-enabled="
                                                (isAllowedToEdit &&
                                                    !newGroup) ||
                                                (newGroup &&
                                                    groupData.isSecretGroup)
                                            "
                                            :action-tooltip="
                                                (user: User) =>
                                                    groupData.isSecretGroup
                                                        ? `${user.firstName} ${user.lastName} nicht geheim Beschenken`
                                                        : `${user.firstName} ${user.lastName} von der Liste entfernen`
                                            "
                                            @action="removeFunction"
                                        />
                                    </v-row>
                                    <v-row>
                                        <group-form-list
                                            :users="usersThatGetRemoved"
                                            title="Zu entfernde Beschenkte"
                                            title-icon="mdi-account-off-outline"
                                            action-icon="mdi-delete-off-outline"
                                            empty-strategy="hide"
                                            :action-enabled="isAllowedToEdit"
                                            :action-tooltip="
                                                (user: User) =>
                                                    `Löschen von ${user.firstName} ${user.lastName} rückgängig machen`
                                            "
                                            @action="undoRemoving"
                                        />
                                    </v-row>
                                </v-container>
                            </v-col>
                            <v-col
                                v-if="
                                    !groupData.isSecretGroup &&
                                    (groupData.editable || newGroup)
                                "
                                class="d-flex justify-center"
                                :cols="cols"
                            >
                                <v-container>
                                    <v-row>
                                        <group-form-list
                                            :users="
                                                groupData.invitations.map(
                                                    (inv) => inv.user,
                                                )
                                            "
                                            :title="'Als Beschenkte eingeladen'"
                                            :title-icon="'mdi-email-fast-outline'"
                                            :action-enabled="isAllowedToEdit"
                                            :action-icon="'mdi-email-off-outline'"
                                            own-action-icon="mdi-email-check-outline"
                                            :own-action-tooltip="
                                                (user: User) =>
                                                    `Einladung annehmen`
                                            "
                                            :action-tooltip="
                                                (user: User) =>
                                                    `Einladung von ${user.firstName} ${user.lastName} zurückziehen`
                                            "
                                            @action="removeFromInvitation"
                                        />
                                    </v-row>
                                </v-container>
                            </v-col>
                            <v-col class="d-flex justify-center" :cols="cols">
                                <v-container>
                                    <v-row>
                                        <group-form-list
                                            :users="giftingUsers"
                                            :group-i-d="groupData.id"
                                            :is-own-group="
                                                groupData.isBeingGifted ||
                                                isAllowedToEditTitle
                                            "
                                            :special-users="
                                                groupData.isSpecialUser
                                            "
                                            title="Schenkende"
                                            title-icon="mdi-gift-outline"
                                            :own-action-enabled="
                                                !groupData.isSecretGroup
                                            "
                                            :action-icon="
                                                groupData.isSecretGroup
                                                    ? 'mdi-gift-open-outline'
                                                    : 'mdi-email-outline'
                                            "
                                            :action-enabled="isAllowedToEdit"
                                            :action-tooltip="
                                                (user: User) =>
                                                    groupData.isSecretGroup
                                                        ? `${user.firstName} ${user.lastName} zum geheim Beschenkten machen`
                                                        : `${user.firstName} ${user.lastName} einladen um beschenkt zu werden`
                                            "
                                            @action="putIntoFunction"
                                            @remove-from-group="
                                                handleRemoveFromGroup
                                            "
                                        />
                                    </v-row>
                                    <v-row v-if="propGroupData.isBeingGifted">
                                        <DashboardCardGuestRegister
                                            v-model="registrationDialog"
                                            :start-viewing-group="
                                                propGroupData.id
                                            "
                                            @registration-finished="
                                                handleRegistrationFinished
                                            "
                                        />
                                        <v-btn
                                            color="primary"
                                            @click="registrationDialog = true"
                                            >Schenkende*n anlegen</v-btn
                                        >
                                    </v-row>
                                </v-container>
                            </v-col>
                            <v-col class="d-flex justify-center" :cols="cols">
                                <v-container>
                                    <v-row>
                                        <group-form-list
                                            :users="addableSpecialUsers"
                                            :group-i-d="groupData.id"
                                            title="Mögliche Schenkende"
                                            title-icon="mdi-gift-outline"
                                            :own-action-enabled="
                                                !groupData.isSecretGroup
                                            "
                                            :action-icon="'mdi-plus'"
                                            :action-enabled="
                                                groupData.isBeingGifted ||
                                                isAllowedToEditTitle
                                            "
                                            :action-tooltip="
                                                (user: User) =>
                                                    `${user.firstName} ${user.lastName} als Schenkende*n hinzufügen`
                                            "
                                            @action="openAddGuestDialog"
                                        />
                                    </v-row>
                                </v-container>
                            </v-col>
                        </v-row>
                    </v-container>
                    <v-container v-if="isAllowedToEditTitle">
                        <v-row justify="center">
                            <v-spacer v-if="!isAllowedToEdit" />
                            <v-btn
                                :color="willDeleteGroup ? 'error' : 'primary'"
                                type="submit"
                            >
                                {{ buttonText }}
                            </v-btn>
                            <v-spacer v-if="!isAllowedToEdit" />
                            <v-btn
                                v-if="!isAllowedToEdit"
                                :color="'error'"
                                @click="deleteGroup"
                            >
                                Liste löschen
                            </v-btn>
                            <v-spacer v-if="!isAllowedToEdit" />
                        </v-row>
                    </v-container>
                </v-form>
            </v-skeleton-loader>
        </v-card>
        <v-dialog v-model="addGuestDialog" max-width="450px">
            <v-card>
                <v-card-title>Gast zugriff gewähren</v-card-title>
                <v-card-text>
                    <v-checkbox-btn
                        v-model="hasExpirationDate"
                        label="Zugriff zeitlich begrenzen"
                    ></v-checkbox-btn>
                    <v-date-input
                        v-if="hasExpirationDate"
                        v-model="expirationDate"
                        :allowed-dates="onlyFutureDates"
                        label="Gast Zugriff gewähren bis"
                        :hide-details="true"
                        :display-format="dateFormat"
                    ></v-date-input>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="addAsGifting">
                        Gast zugriff gewähren
                    </v-btn>
                    <v-btn color="primary" @click="addGuestDialog = false">
                        Abbrechen
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <v-snackbar v-model="sharelinkSnackbar" :timeout="5000" color="success">
            {{ shareLink }} ins Clipboard kopiert
        </v-snackbar>
    </v-dialog>
</template>
<script setup lang="ts">
const addGuestDialog = ref(false);
const hasExpirationDate = ref(false);
const expirationDate = ref("");
const userStore = useUserStore();
const giftgroupStore = useGiftGroupStore();
const { data } = useAuth();
const registrationDialog = ref(false);
const baseUrl = window.location.origin;
//*********************************************************************//
//-------------------------------- Data -------------------------------//
//*********************************************************************//
const form = ref(null);
function someoneIsBeingGiftedRule(): boolean | string {
    if (
        !outerProps.newGroup ||
        !groupData.value.isSecretGroup ||
        (groupData.value.usersBeingGifted &&
            groupData.value.usersBeingGifted.length > 0)
    )
        return true;
    return "Mindestens eine Person muss geheim beschenkt werden";
}

const groupDialog = defineModel<boolean>("groupDialog", { default: false });
const emit = defineEmits(["submitForm", "joinGroup"]);
const outerProps = defineProps({
    propGroupData: {
        type: Object as PropType<Giftgroup>,
        default: () => ({
            name: "",
            isSecretGroup: false,
            invitations: () => [],
            giftgroup_id: -1,
        }),
    },
    newGroup: {
        type: Boolean,
        default: true,
    },
    usersLoaded: {
        type: Boolean,
        required: true,
    },
});
const groupData = ref<
    Omit<Giftgroup, "invitations"> & {
        invitations: { user: User; fullname: string }[];
    }
>({
    ...outerProps.propGroupData,
    invitations:
        outerProps.propGroupData.invitations?.map((user) => ({
            user: user,
            fullname: `${user.firstName} ${user.lastName}`,
        })) ?? [],
});
let usersBeingGiftedSwap = [] as User[];
let invitationSwap = [] as { user: User; fullname: string }[];
watch(
    () => groupData.value.isSecretGroup,
    () => {
        if (outerProps.newGroup) {
            const usersBeingGiftedTemp = groupData.value.usersBeingGifted ?? [];
            groupData.value.usersBeingGifted = usersBeingGiftedSwap;
            usersBeingGiftedSwap = usersBeingGiftedTemp;
            const invitationsTemp = groupData.value.invitations;
            groupData.value.invitations = invitationSwap;
            invitationSwap = invitationsTemp;
        }
    },
);
watch(
    () => {
        return groupData.value.usersBeingGifted
            ? groupData.value.usersBeingGifted.length
            : 0;
    },
    () => {
        if (form.value) (form.value as any).validate();
    },
);
watch(outerProps, (newVal) => {
    for (const [key, value] of Object.entries(
        newVal.propGroupData as Giftgroup,
    )) {
        if (key === "invitations") {
            groupData.value.invitations = (value as User[]).map((user) => ({
                user: user,
                fullname: `${user.firstName} ${user.lastName}`,
            }));
        } else {
            (groupData.value as any)[key] = value;
        }
    }
});
watch(
    () => outerProps.usersLoaded,
    (newVal) => {
        if (newVal === true) {
            const thisUser = userStore.users.find(
                (user) => user.email === (data.value as any).email,
            )!;
            if (outerProps.newGroup) {
                groupData.value["usersBeingGifted"] = [thisUser];
            }
        }
    },
);
async function deleteGroup() {
    groupData.value.usersBeingGifted = [];
    emit("submitForm", {
        ...groupData.value,
    });
}
async function submitForm(event: any) {
    const results = await event;
    if (results.valid) {
        const invitations = groupData.value.invitations.map(
            (user) => user.user,
        );
        emit("submitForm", {
            ...groupData.value,
            invitations: invitations,
        });
        usersThatGetRemoved.value = [];
    }
}

//*********************************************************************//
//-------------------------------- Share ------------------------------//
//*********************************************************************//

const shareButtonStyle = computed(() => {
    if (lgAndUp.value) {
        return "height: 100%;";
    }
    return "width: 100%";
});

const shareCols = computed(() => {
    if (lgAndUp.value) {
        return 3;
    }
    return 12;
});
function dateFormat(date: Date): string {
    return date.toLocaleDateString();
}

const onlyFutureDates = (date: unknown) => {
    if (!(date instanceof Date)) {
        return false;
    }
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Strip time for accurate comparison
    const selectedDate = new Date(date);
    return selectedDate >= today;
};

watch(
    () => outerProps.propGroupData.shareTokenExpireDate,
    (newVal) => {
        shareTokenDate.value = newVal;
    },
);
const shareTokenDate = ref(outerProps.propGroupData.shareTokenExpireDate);
const sharelinkSnackbar = ref(false);
function deleteShareToken() {
    giftgroupStore.deleteShareToken(groupData.value.id);
    groupData.value.shareToken = "";
    shareTokenDate.value = undefined;
    groupData.value.shareTokenExpireDate = shareTokenDate.value;
}

async function generateShareToken() {
    if (shareTokenDate.value) {
        groupData.value.shareToken = await giftgroupStore.generateShareToken(
            groupData.value.id,
            shareTokenDate.value,
        );
        groupData.value.shareTokenExpireDate = shareTokenDate.value;
    }
}

async function changeShareTokenDate() {
    if (shareTokenDate.value) {
        await giftgroupStore.updateShareTokenExpireDate(
            groupData.value.id,
            shareTokenDate.value,
        );
        groupData.value.shareTokenExpireDate = shareTokenDate.value;
    }
}
const shareLink = computed(
    () => `${baseUrl}/shared?shareToken=${groupData.value.shareToken}`,
);
function copyShareLinkToClipboard() {
    navigator.clipboard.writeText(shareLink.value);
    sharelinkSnackbar.value = true;
}

//*********************************************************************//
//-------------------------------- Visual -----------------------------//
//*********************************************************************//
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();
const showInviteCol = computed(
    () => groupData.value.editable || outerProps.newGroup,
);
const cols = computed(() => {
    if (lgAndUp.value) {
        if (showInviteCol.value && !groupData.value.isSecretGroup) return 3;
        else return 4;
    }
    return 12;
});
const buttonText = computed(() => {
    if (willDeleteGroup.value) return "Liste löschen";
    else return "Liste speichern";
});
const isOwner = computed(
    () =>
        groupData.value.isBeingGifted ||
        (!groupData.value.isBeingGifted && groupData.value.isSecretGroup),
);
const isAllowedToEditTitle = computed(
    () =>
        isAllowedToEdit.value ||
        (groupData.value.editable &&
            !groupData.value.isBeingGifted &&
            groupData.value.isSecretGroup),
);
const isAllowedToEdit = computed(
    () =>
        outerProps.newGroup ||
        (groupData.value.editable && groupData.value.isBeingGifted),
);
const willDeleteGroup = computed(
    () =>
        !outerProps.newGroup &&
        groupData.value.usersBeingGifted &&
        groupData.value.usersBeingGifted.length === 0,
);

//**********************************************************************//
//-------------------------------- Lists -------------------------------//
//**********************************************************************//
//---------------- Gifted ----------------//
const usersThatGetRemoved = ref([] as User[]);
const removeFunction = computed(() =>
    groupData.value.isSecretGroup
        ? removeFromBeingGiftedAndPutIntoGifting
        : removeFromBeingGifted,
);
function removeFromBeingGiftedAndPutIntoGifting(user: User) {
    if (groupData.value.usersBeingGifted) {
        groupData.value.usersBeingGifted.splice(
            groupData.value.usersBeingGifted.findIndex((usr) => usr === user),
            1,
        );
    }
}
function removeFromBeingGifted(user: User) {
    const index = groupData.value.usersBeingGifted?.findIndex(
        (usr) => usr.email === user.email,
    );
    if (
        usersThatGetRemoved.value.find(
            (rem_user) => rem_user.email === user.email,
        ) ||
        index === undefined ||
        index === -1
    )
        return;
    usersThatGetRemoved.value.push(user);
    groupData.value.usersBeingGifted!.splice(index, 1);
}
function undoRemoving(user: User) {
    const index = usersThatGetRemoved.value.findIndex(
        (rem_user) => rem_user === user,
    );
    if (index === -1) return;
    groupData.value.usersBeingGifted!.push(user);
    usersThatGetRemoved.value.splice(index, 1);
}
//---------------- Invited ----------------//
function removeFromInvitation(user: User) {
    if (
        user.email === (data.value as any).email &&
        !usersThatGetRemoved.value.find((usr) => usr.email === user.email)
    )
        joinGroup();
    else
        groupData.value.invitations.splice(
            groupData.value.invitations.findIndex(
                (invitation) => invitation.user === user,
            ),
            1,
        );
}
function joinGroup() {
    emit("joinGroup");
}
//---------------- Gifting ----------------//
const giftingUsers = computed(() =>
    userStore.users.filter(
        (user) =>
            !(
                user.onlyViewing &&
                !groupData.value.isSpecialUser?.includes(user.email)
            ) &&
            !groupData.value.invitations.find(
                (invitedUser) => invitedUser.user.email === user.email,
            ) &&
            !groupData.value.usersBeingGifted?.find(
                (beingGiftedUser) => beingGiftedUser.email === user.email,
            ),
    ),
);
const putIntoFunction = computed(() =>
    groupData.value.isSecretGroup ? putIntoBeingGifted : putIntoInvitation,
);
function putIntoInvitation(user: User) {
    groupData.value.invitations.push({
        user: user,
        fullname: `${user.firstName} ${user.lastName}`,
    });
}
function putIntoBeingGifted(user: User) {
    if (!groupData.value.usersBeingGifted)
        groupData.value.usersBeingGifted = [];
    groupData.value.usersBeingGifted.push(user);
}
//---------------- SpecialUser ----------------//
const addableSpecialUsers = computed(() =>
    userStore.users.filter(
        (user) =>
            user.onlyViewing &&
            !groupData.value.isSpecialUser?.includes(user.email),
    ),
);
let openedGuestUser: User | null = null;
function openAddGuestDialog(user: User) {
    openedGuestUser = user;
    addGuestDialog.value = true;
}
function addAsGifting() {
    const user = openedGuestUser as User;
    giftgroupStore.addSpecialUser(outerProps.propGroupData, user.email);
    if (!groupData.value.isSpecialUser) groupData.value.isSpecialUser = [];
    groupData.value.isSpecialUser.push(user.email);
    addGuestDialog.value = false;
    openedGuestUser = null;
}
function handleRemoveFromGroup(user: User) {
    giftgroupStore.removeFromGroup(outerProps.propGroupData, user.email);
    groupData.value.isSpecialUser!.splice(
        groupData.value.isSpecialUser!.findIndex((usr) => usr === user.email),
        1,
    );
}
function handleRegistrationFinished(user_email: string) {
    if (!groupData.value.isSpecialUser) groupData.value.isSpecialUser = [];
    groupData.value.isSpecialUser.push(user_email);
}
</script>
