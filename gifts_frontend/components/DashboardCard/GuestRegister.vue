<template>
    <v-dialog v-model="registrationDialog" max-width="450px">
        <v-card width="100%" class="mx-auto pa-7">
            <v-alert
                v-if="registerAlert.text || registerAlert.title"
                color="error"
                icon="$error"
                :text="registerAlert.text"
                :title="registerAlert.title"
                class="ma-2"
            />
            <v-form
                validate-on="blur lazy"
                @submit.prevent="handleRegistrationClick"
            >
                <v-text-field
                    v-model="registrationFormRef.firstName"
                    label="Vorname/Alias"
                    :rules="[nonEmptyRule('Vorname')]"
                />
                <v-checkbox-btn
                    v-model="registrationFormRef.useExpirationDate"
                    label="Zugriff zeitlich begrenzen"
                ></v-checkbox-btn>
                <v-date-input
                    v-if="registrationFormRef.useExpirationDate"
                    v-model="registrationFormRef.dateUntil"
                    :allowed-dates="onlyFutureDates"
                    label="Gast Zugriff gewähren bis"
                    :hide-details="true"
                    :display-format="dateFormat"
                ></v-date-input>
                <v-btn
                    color="primary"
                    :loading="loading"
                    type="submit"
                    block
                    class="mt-2"
                >
                    Gast anlegen
                </v-btn>
                <v-btn
                    color="primary"
                    :loading="loading"
                    block
                    class="mt-2"
                    @click="registrationDialog = false"
                >
                    Schließen
                </v-btn>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
import { v4 as uuidv4 } from "uuid";
const loading = ref(false);
const userStore = useUserStore();
const giftgroupStore = useGiftGroupStore();

const props = defineProps({
    startViewingGroup: { type: Number, required: false, default: null },
});

const onlyFutureDates = (date: unknown) => {
    if (!(date instanceof Date)) {
        return false;
    }
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(date);
    return selectedDate >= today;
};
function dateFormat(date: Date): string {
    return date.toLocaleDateString();
}

const registrationDialog = defineModel<boolean>();
const registrationFormRef = ref({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    useExpirationDate: false,
    dateUntil: "" as Date | string,
});

const registerAlert = ref({} as { title: string; text: string });
const emits = defineEmits(["registrationFinished"]);
async function handleRegistrationClick(event: any) {
    loading.value = true;
    const results = await event;
    loading.value = false;
    if (results.valid) {
        try {
            (registrationFormRef.value as any).startViewingGroup =
                props.startViewingGroup;
            (registrationFormRef.value as any).onlyViewing = true;
            (registrationFormRef.value as any).email = `${uuidv4()}@guest.com`;
            (registrationFormRef.value as any).password = uuidv4();
            if (!registrationFormRef.value.useExpirationDate) {
                (registrationFormRef.value as any).dateUntil = "";
            } else {
                const localDate = new Date(
                    (registrationFormRef.value.dateUntil as Date).getTime() -
                        (
                            registrationFormRef.value.dateUntil as Date
                        ).getTimezoneOffset() *
                            60000,
                )
                    .toISOString()
                    .split("T")[0];
                (registrationFormRef.value as any).dateUntil = localDate;
            }
            const _ = await userStore.createUser(registrationFormRef.value);
            registerAlert.value = {} as { title: string; text: string };
        } catch (e: any) {
            switch (e.response.status) {
                case 406:
                    registerAlert.value.title = "email existiert bereits!";
                    break;
                default:
                    registerAlert.value.title =
                        "unbekannter Fehler: " + e.response;
            }
        } finally {
            registrationDialog.value = false;
            await giftgroupStore.loadFromAPI();
            emits("registrationFinished", registrationFormRef.value.email);
        }
    }
}
</script>

<style lang="scss">
.password-strength {
    height: 4px;
    transition-property: width, background-color;
    transition-duration: 0.7s;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
