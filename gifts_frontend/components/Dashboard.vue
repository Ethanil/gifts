<template>
  <v-card>
    <div class="d-flex flex-row">
      <v-navigation-drawer>
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
      </v-navigation-drawer>
      <v-card class="ma-auto">
        <v-data-table
          :class="{ 'ma-4': true }"
          :headers="tableHeaders"
          :items="giftStore?.getGiftsOfCurrentGroup"
          items-per-page="-1"
        >
          <template #[`item.picture`]="{ item }">
            <v-card class="my-2" rounded>
              <v-img
                :src="(item.picture as string)"
                height="64"
                width="96"
                cover
              ></v-img>
            </v-card>
            <!-- <v-img :src="(item.picture as string)" cover /> -->
          </template>
          <template #[`item.giftStrength`]="{ item }">
            <v-rating
              v-model="item.giftStrength"
              color="primary"
              :disabled="true"
              density="compact"
              size="small"
            ></v-rating>
          </template>
          <template #item.availableActions="{ item }">
            <v-container>
              <v-row no-gutters>
                <v-tooltip
                  v-if="item.availableActions.includes('edit')"
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
                  v-if="item.availableActions.includes('delete')"
                  text="Geschenk löschen"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="openDeleteConfirmationDialog(item)"
                      >
                        mdi-delete
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="item.availableActions.includes('reserve')"
                  text="Geschenk reservieren"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { reserve: true })"
                      >
                        mdi-lock
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="item.availableActions.includes('stop reserve')"
                  text="Reservierung löschen"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { reserve: false })"
                      >
                        mdi-lock-off
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="item.availableActions.includes('free reserve')"
                  text="Zur Reservierung freigeben"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { freeReserve: true })"
                      >
                        mdi-share
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="item.availableActions.includes('stop free reserve')"
                  text="Nicht mehr zur Reservierung freigeben"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { freeReserve: false })"
                      >
                        mdi-share-off
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="item.availableActions.includes('request free reserve')"
                  text="Reservierungs freigabe erbitten"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { requestFreeReserve: true })"
                      >
                        mdi-back-right
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
                <v-tooltip
                  v-if="
                    item.availableActions.includes('stop request free reserve')
                  "
                  text="Nicht mehr Reservierungs freigabe erbitten"
                  location="bottom"
                >
                  <template #activator="{ props }">
                    <v-col>
                      <v-icon
                        v-bind="props"
                        size="large"
                        @click="do_Action(item, { requestFreeReserve: false })"
                      >
                        mdi-back-right-off
                      </v-icon>
                    </v-col>
                  </template>
                </v-tooltip>
              </v-row>
            </v-container>
          </template>
          <template #bottom></template>
        </v-data-table>
        <gift-form
          v-model:gift-data="giftDataToAdd"
          :prop-gift-data="giftDataToAdd"
          @submit-form="addGift"
        >
          <template #activator="{ props }">
            <v-btn color="primary" v-bind="props"> Geschenk Hinzufügen </v-btn>
          </template>
        </gift-form>
      </v-card>
    </div>
    <gift-form
      v-model:gift-dialog="editDialog"
      v-model:gift-data="giftDataToEdit"
      :prop-gift-data="giftDataToEdit"
      @submit-form="updateGift"
    ></gift-form>
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
          <v-btn color="primary" @click="deleteConfirmationDialog = false">
            Abbrechen
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>
<script setup lang="ts">
//---------------- Edit ----------------//
const editDialog = ref(false);
const giftDataToEdit = ref<Gift>({} as Gift);
async function updateGift(gift: Gift) {
  await giftStore.updateGift(gift);
}
function editGift(gift: Gift) {
  giftDataToEdit.value = gift;
  editDialog.value = true;
}

//---------------- Table ----------------//
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

//---------------- Add ----------------//
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
}

//---------------- Delete ----------------//
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

//---------------- Reserve, Free Reserve, Request Free Reserve ----------------//
function do_Action(
  gift: Gift,
  queryParams: {
    reserve?: boolean;
    freeReserve?: boolean;
    requestFreeReserve?: boolean;
  }
) {
  giftStore.doAction(gift, queryParams);
}
</script>
