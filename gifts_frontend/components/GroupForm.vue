<template>
    <v-dialog
        v-model="groupDialog"
        :max-width="showInviteCol ? '900px' : '600px'"
    >
        <template #activator="{ props }">
            <slot name="activator" :props="props" />
        </template>
        <v-card>
            <div class="v-system-bar">
                <v-icon @click="groupDialog = false"> mdi-close </v-icon>
            </div>
            <v-alert v-if="willDeleteGroup" type="error">
                DIE LISTE WIRD GELÖSCHT
            </v-alert>
            <v-form class="pa-5 pt-3" @submit.prevent="submitForm">
                <template v-if="isAllowedToEdit">
                    <v-text-field
                        v-model="groupData.name"
                        label="Name der Liste"
                        :rules="[nonEmptyRule('Name der Liste')]"
                    />
                </template>
                <v-card-title v-else>
                    {{ title }}
                </v-card-title>
                <v-container>
                    <v-row no-gutters>
                        <v-col :cols="cols">
                            <group-form-list
                                :users="groupData.usersBeingGifted ?? []"
                                title="Beschenkte"
                                title-icon="mdi-gift-open-outline"
                                action-icon="mdi-delete-outline"
                                :action-enabled="isAllowedToEdit && !newGroup"
                                :action-tooltip="
                                    (user: User) =>
                                        `${user.firstName} ${user.lastName} von der Liste entfernen`
                                "
                                @action="removeFromBeingGifted"
                            />
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
                        </v-col>
                        <v-col
                            v-if="groupData.editable || newGroup"
                            :cols="cols"
                        >
                            <group-form-list
                                :users="
                                    groupData.invitations.map((inv) => inv.user)
                                "
                                title="Als Beschenkte eingeladen"
                                title-icon="mdi-email-fast-outline"
                                :action-enabled="isAllowedToEdit"
                                action-icon="mdi-email-off-outline"
                                own-action-icon="mdi-email-check-outline"
                                :own-action-tooltip="
                                    (user: User) => `Einladung annehmen`
                                "
                                :action-tooltip="
                                    (user: User) =>
                                        `Einladung von ${user.firstName} ${user.lastName} zurückziehen`
                                "
                                @action="removeFromInvitation"
                            />
                        </v-col>
                        <v-col :cols="cols">
                            <group-form-list
                                :users="giftingUsers"
                                title="Schenkende"
                                title-icon="mdi-gift-outline"
                                action-icon="mdi-email-outline"
                                :action-enabled="isAllowedToEdit"
                                :action-tooltip="
                                    (user: User) =>
                                        `${user.firstName} ${user.lastName} einladen um beschenkt zu werden`
                                "
                                @action="putIntoInvitation"
                            />
                        </v-col>
                    </v-row>
                </v-container>
                <v-container v-if="isAllowedToEdit">
                    <v-row justify="center">
                        <v-btn
                            :color="willDeleteGroup ? 'error' : 'primary'"
                            type="submit"
                        >
                            {{ buttonText }}
                        </v-btn>
                    </v-row>
                </v-container>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
import { useDisplay } from "vuetify";
const { data } = useAuth();
const { lgAndUp } = useDisplay();
const showInviteCol = computed(
    () => groupData.value.editable || outerProps.newGroup,
);
const cols = computed(() => {
    if (lgAndUp.value) {
        if (showInviteCol.value) return 4;
        else return 6;
    }
    return 12;
});
//---------------- Form-Data ----------------//
const userStore = useUserStore();
const isAllowedToEdit = computed(
    () =>
        outerProps.newGroup ||
        (groupData.value.editable && groupData.value.isBeingGifted),
);
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
const willDeleteGroup = computed(
    () =>
        !outerProps.newGroup &&
        groupData.value.usersBeingGifted &&
        groupData.value.usersBeingGifted.length === 0,
);
const buttonText = computed(() => {
    if (willDeleteGroup.value) return "Liste löschen";
    else return "Liste speichern";
});
onMounted(async () => {
    await userStore.loadFromAPI();
    const thisUser = userStore.users.find(
        (user) => user.email === (data.value as any).email,
    )!;
    if (outerProps.newGroup) {
        if (groupData.value.usersBeingGifted) {
            groupData.value.usersBeingGifted?.push(thisUser);
        } else {
            groupData.value["usersBeingGifted"] = [thisUser];
        }
    }
});
const outerProps = defineProps({
    propGroupData: {
        type: Object as PropType<Giftgroup>,
        default: () => ({
            name: "",
            invitations: () => [],
            giftgroup_id: -1,
        }),
    },
    newGroup: {
        type: Boolean,
        default: true,
    },
});
const title = computed(() =>
    outerProps.newGroup
        ? "Neue Geschenkliste erstellen"
        : outerProps.propGroupData.name,
);
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

//---------------- Functionality ----------------//
//---------------- Join Group ----------------//
function joinGroup() {
    emit("joinGroup");
}
const groupDialog = defineModel<boolean>("groupDialog", { default: false });
const emit = defineEmits(["submitForm", "joinGroup"]);
async function submitForm(event: any) {
    const results = await event;
    if (results.valid) {
        const invitations = groupData.value.invitations.map(
            (user) => user.user,
        );
        emit("submitForm", { ...groupData.value, invitations: invitations });
        usersThatGetRemoved.value = [];
    }
}
function putIntoInvitation(user: User) {
    groupData.value.invitations.push({
        user: user,
        fullname: `${user.firstName} ${user.lastName}`,
    });
}
function removeFromInvitation(user: User) {
    if (user.email === (data.value as any).email) joinGroup();
    else
        groupData.value.invitations.splice(
            groupData.value.invitations.findIndex(
                (invitation) => invitation.user === user,
            ),
            1,
        );
}
const usersThatGetRemoved = ref([] as User[]);
function removeFromBeingGifted(user: User) {
    const index = groupData.value.usersBeingGifted?.findIndex(
        (usr) => usr === user,
    );
    if (
        usersThatGetRemoved.value.find((rem_user) => rem_user === user) ||
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
</script>
