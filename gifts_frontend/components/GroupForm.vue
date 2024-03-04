<template>
    <v-dialog
        v-model="groupDialog"
        :max-width="showInviteCol ? '900px' : '600px'"
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
                        diese Gruppe nicht sehen!</span
                    >
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
    </v-dialog>
</template>
<script setup lang="ts">
const userStore = useUserStore();
const { data } = useAuth();

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
            console.log(groupData.value["usersBeingGifted"]);
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
//-------------------------------- Visual -----------------------------//
//*********************************************************************//
import { useDisplay } from "vuetify";
const { lgAndUp } = useDisplay();
const showInviteCol = computed(
    () => groupData.value.editable || outerProps.newGroup,
);
const cols = computed(() => {
    if (lgAndUp.value) {
        if (showInviteCol.value && !groupData.value.isSecretGroup) return 4;
        else return 6;
    }
    return 12;
});
const buttonText = computed(() => {
    if (willDeleteGroup.value) return "Liste löschen";
    else return "Liste speichern";
});
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
</script>
