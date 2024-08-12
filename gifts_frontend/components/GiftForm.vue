<template>
    <v-dialog v-model="giftDialog" max-width="650px">
        <template #activator="{ props }">
            <slot name="activator" :props="props" />
        </template>
        <v-card>
            <div class="v-system-bar">
                <v-icon icon="mdi-close" @click="giftDialog = false" />
            </div>
            <v-form
                class="pa-5"
                validate-on="blur lazy"
                @submit.prevent="submitForm"
            >
                <v-text-field
                    v-model="giftData.name"
                    label="Name des Geschenks"
                    counter="60"
                    :rules="[
                        nonEmptyRule('Name des Geschenks'),
                        maxCharRule(60),
                    ]"
                />
                <v-text-field
                    v-model="giftData.description"
                    counter="255"
                    label="Beschreibung des Geschenks"
                    :rules="[maxCharRule(255)]"
                />
                <v-text-field
                    v-model="giftData.link"
                    label="Link des Geschenks"
                />
                <v-rating
                    v-model="giftData.giftStrength"
                    hover
                    :item-labels="['Ganz okay', 'Okay', 'Gut', 'Super', 'Mega']"
                    :length="5"
                    active-color="primary"
                />
                <v-text-field
                    v-model.number="giftData.price"
                    label="Preis des Geschenks"
                    suffix="€"
                    :rules="[isNumberRule('Preis')]"
                />
                <v-container>
                    <v-row>
                        <v-col cols="7" align-self="center">
                            <v-container>
                                <v-row
                                    ><v-checkbox
                                        v-model="is_url_picture"
                                        label="URL als Bild verwenden"
                                        color="primary"
                                    ></v-checkbox
                                ></v-row>
                                <v-row v-if="!is_url_picture"
                                    ><v-file-input
                                        v-model="giftImage"
                                        accept="image/png, image/jpeg, image/bmp"
                                        label="Bild des Geschenks"
                                        :rules="[uploadRule]"
                                        :clearable="true"
                                        @update:model-value="
                                            handleImageInput(giftImage)
                                        "
                                /></v-row>
                                <v-row v-else
                                    ><v-text-field
                                        v-model="giftData.picture"
                                        label="Bild-URL"
                                    >
                                    </v-text-field
                                ></v-row>
                            </v-container>
                        </v-col>
                        <v-col
                            cols="3"
                            align-self="center"
                            align-content="center"
                            offset="1"
                        >
                            <v-img
                                :src="giftData.picture as string"
                                max-height="64px"
                            />
                        </v-col>
                    </v-row>
                    <v-row justify="center">
                        <v-btn color="primary" type="submit">
                            {{ submitText }}
                        </v-btn>
                    </v-row>
                </v-container>
            </v-form>
        </v-card>
    </v-dialog>
</template>
<script setup lang="ts">
import type { PropType } from "vue";
import maxCharRule from "~/utils/maxCharRule";
const emit = defineEmits(["submitForm"]);
const giftDialog = defineModel<boolean>("giftDialog", {
    type: Boolean,
    default: false,
});
const uploadRule = (value: File[] | undefined) => {
    return (
        !value ||
        !value.length ||
        value[0].size < 2000000 ||
        "Bilder dürfen maximal 2MB groß sein!"
    );
};
// Form-Data
const outerProps = defineProps({
    propGiftData: {
        type: Object as PropType<Gift>,
        default: () => ({
            id: 0,
            name: "",
            price: 0,
            giftStrength: 3,
            description: "",
            link: "",
            picture: "",
            availableActions: () => [],
        }),
    },
    submitText: {
        type: String,
        default: "Geschenk hinzufügen",
    },
});
const giftImage = ref<File[] | undefined>(undefined);
const isBase64String = (val: string) => {
    if (!val || typeof val !== "string") return false;
    let splitData = val.split(",");
    if (splitData.length != 2) return false;
    splitData = splitData[0].split(":");
    if (splitData.length != 2) return false;
    splitData = splitData[1].split(";");
    if (splitData.length != 2) return false;
    return true;
};
const is_url_picture = ref<boolean>(false);

watch(outerProps, (newVal) => {
    for (const [key, value] of Object.entries(newVal.propGiftData as Gift)) {
        (giftData.value as any)[key] = value;
    }
});

watch(outerProps.propGiftData, (newVal) => {
    is_url_picture.value = !isBase64String(newVal.picture as string);
});

const giftData = ref<Gift>(outerProps.propGiftData);

async function handleImageInput(files: File[] | undefined) {
    if (!files || files.length != 1) {
        giftData.value.picture = "";
        return;
    }
    const image = files[0];
    const type = image.type.split("/");
    if (type[0] !== "image" || (type[1] !== "jpeg" && type[1] !== "png")) {
        giftData.value.picture = "";
        return;
    }
    const reader = new FileReader();
    reader.readAsDataURL(image);
    reader.onload = () => {
        giftData.value.picture = reader.result as string;
    };
}
const b64toBlob = (b64String: string, contentType = "", sliceSize = 512) => {
    let splitData = b64String.split(",");
    const b64Data = splitData[1];
    splitData = splitData[0].split(":");
    splitData = splitData[1].split(";");
    contentType = splitData[0];
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    const blob = new Blob(byteArrays, { type: contentType });
    return blob;
};
async function submitForm(event: any) {
    const results = await event;
    if (results.valid) {
        let picture;
        if (isBase64String(giftData.value.picture as string))
            picture = b64toBlob(giftData.value.picture as string) as File;
        else picture = giftData.value.picture;
        const gift = {
            id: giftData.value.id,
            name: giftData.value.name,
            price: giftData.value.price,
            giftStrength: +giftData.value.giftStrength,
            description: giftData.value.description,
            link: giftData.value.link,
            picture: picture,
            availableActions: [],
        } as Gift;
        emit("submitForm", gift);
        giftImage.value = undefined;
    }
}
</script>
