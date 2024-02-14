<template>
  <v-dialog v-model="giftDialog" width="50%">
    <template #activator="{ props }">
      <slot name="activator" :props="props"></slot>
    </template>
    <v-card class="pa-5">
      <v-form @submit.prevent="submitForm">
        <v-text-field
          v-model="giftData.name"
          label="Name des Geschenks"
        ></v-text-field>
        <v-text-field
          v-model="giftData.description"
          label="Beschreibung des Geschenks"
        ></v-text-field>
        <v-text-field
          v-model="giftData.link"
          label="Link des Geschenks"
        ></v-text-field>
        <v-rating
          hover
          v-model="giftData.giftStrength"
          :item-labels="['Ganz okay', 'Okay', 'Gut', 'Super', 'Mega']"
          :length="5"
          active-color="primary"
        ></v-rating>
        <v-text-field
          v-model.number="giftData.price"
          label="Preis des Geschenks"
        ></v-text-field>
        <v-container>
          <v-row>
            <v-col cols="4" align-self="center">
              <v-file-input
                v-model="giftImage"
                accept="image/png, image/jpeg, image/bmp"
                :rules="uploadRules"
                :clearable="true"
                @update:model-value="handleImageInput(giftImage)"
              />
            </v-col>
            <v-col cols="2" offset="6">
              <v-img :src="base64Image" />
            </v-col>
          </v-row>
        </v-container>
        <v-btn color="primary" type="submit"> Geschenk hinzufügen </v-btn>
      </v-form>
    </v-card>
  </v-dialog>
</template>
<script setup lang="ts">
const emit = defineEmits(["submitForm"]);
const giftDialog = defineModel("giftDialog", { default: false });
// const addGiftDialog = ref(false);
const uploadRules = [
  (value: File[] | undefined) => {
    return (
      !value ||
      !value.length ||
      value[0].size < 2000000 ||
      "Bilder dürfen maximal 2MB groß sein!"
    );
  },
];
// Form-Data
const giftImage = ref<File[] | undefined>(undefined);
const base64Image = ref("");

const giftData = defineModel("giftData", {
  default: {
    name: "",
    price: 0,
    giftStrength: 3,
    description: "",
    link: "",
    picture: "",
    availableActions: [],
  },
});

async function handleImageInput(files: File[] | undefined) {
  if (!files || files.length != 1) {
    base64Image.value = "";
    return;
  }
  const image = files[0];
  const type = image.type.split("/");
  if (type[0] !== "image" || (type[1] !== "jpeg" && type[1] !== "png")) {
    base64Image.value = "";
    return;
  }
  const reader = new FileReader();
  reader.readAsDataURL(image);
  reader.onload = () => {
    base64Image.value = reader.result as string;
  };
}

async function submitForm() {
  const gift = {
    name: giftData.value.name,
    price: giftData.value.price,
    giftStrength: giftData.value.giftStrength,
    description: giftData.value.description,
    link: giftData.value.link,
    picture: giftImage.value?[0] : "",
    availableActions: [],
  } as Gift;
  emit("submitForm", gift);
  giftDialog.value = false;
}
</script>
