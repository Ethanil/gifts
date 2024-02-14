<template>
  <v-card>
    <div class="d-flex flex-row">
      <v-tabs v-model="currentTab" direction="vertical">
        <template v-for="(group, key) in giftgroups" :key="key">
          <v-tab :value="key">
            {{ group.name }}
            <template v-if="group.editable && group.isBeingGifted" #append>
              <v-btn
                variant="text"
                icon="mdi-pencil"
                size="small"
                @click.stop=""
              ></v-btn>
            </template>
          </v-tab>
        </template>
      </v-tabs>
      <v-card>
        <v-data-table
          class="ma-4"
          :headers="tableHeaders"
          :items="giftStore?.getGiftsOfCurrentGroup"
          items-per-page="-1"
        >
          <template #[`item.picture`]="{ item }">
            <v-img :src="(item.picture as string)" />
          </template>
          <template #[`item.giftStrength`]="{ item }">
            <v-rating v-model="item.giftStrength" color="primary" :disabled="true" density="compact" size="small"></v-rating>
          </template>
          <template #item.availableActions="{ item }">
            <v-tooltip
              v-if="item.availableActions.includes('edit')"
              text="Geschenk bearbeiten"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon v-bind="props" @click="editGift(item)">
                  mdi-pencil
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('delete')"
              text="Geschenk löschen"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon v-bind="props" @click="deleteGift(item)">
                  mdi-delete
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('reserve')"
              text="Geschenk reservieren"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { reserve: true })"
                >
                  mdi-lock
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('stop reserve')"
              text="Reservierung löschen"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { reserve: false })"
                >
                  mdi-lock-off
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('free reserve')"
              text="Zur Reservierung freigeben"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { freeReserve: true })"
                >
                  mdi-share
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('stop free reserve')"
              text="Nicht mehr zur Reservierung freigeben"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { freeReserve: false })"
                >
                  mdi-share-off
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('request free reserve')"
              text="Reservierungs freigabe erbitten"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { requestFreeReserve: true })"
                >
                  mdi-back-right
                </v-icon>
              </template>
            </v-tooltip>
            <v-tooltip
              v-if="item.availableActions.includes('stop request free reserve')"
              text="Nicht mehr Reservierungs freigabe erbitten"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  @click="do_Action(item, { requestFreeReserve: false })"
                >
                  mdi-back-right-off
                </v-icon>
              </template>
            </v-tooltip>
          </template>
          <template #bottom></template>
        </v-data-table>
        <gift-form v-model:gift-data="giftDataToAdd" @submit-form="addGift">
          <template #activator="{ props }">
            <v-btn color="primary" v-bind="props"> Geschenk Hinzufügen </v-btn>
          </template>
        </gift-form>
      </v-card>
      <gift-form
        v-model:gift-dialog="editDialog"
        v-model:gift-data="giftDataToEdit"
      ></gift-form>
    </div>
  </v-card>
</template>
<script setup lang="ts">
const editDialog = ref(false);
const giftDataToEdit = ref<Gift>({} as Gift);
const currentTab = ref(0);
const tableHeaders = [
  { title: "Bild", value: "picture" },
  { title: "Name", value: "name" },
  { title: "Beschreibung", value: "description" },
  { title: "Link", value: "link" },
  { title: "Preis", value: "price" },
  { title: "Wunschstärke", value: "giftStrength" },
  { title: "Aktionen", value: "availableActions" },
];
const giftgroups = computed(() => {
  return giftgroupStore.$state.giftgroups;
});
const giftgroupStore = useGiftGroupStore();
const giftStore = useGiftStore();
onMounted(() => {
  giftgroupStore.loadFromAPI().then(() => {
    giftStore.loadFromAPI();
    giftStore.setGroup(giftgroupStore.giftgroups[0].id);
  });
});
watch(currentTab, (newValue) =>
  giftStore.setGroup(giftgroupStore.giftgroups[newValue].id)
);

const giftDataToAdd = ref<Gift>({
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
}

function editGift(gift: DatabaseGift) {
  giftDataToEdit.value = gift;
  editDialog.value = true;
}
function deleteGift(gift: DatabaseGift) {}
function do_Action(
  gift: DatabaseGift,
  queryParams: {
    reserve?: boolean;
    freeReserve?: boolean;
    requestFreeReserve?: boolean;
  }
) {
  giftStore
    .doAction(gift, giftgroupStore.getGiftgroups[currentTab.value], queryParams)
    .then(() => {
      giftStore.loadFromAPI();
    });
}
</script>
