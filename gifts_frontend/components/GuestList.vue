<template>
  <v-card class="mx-auto" max-width="800">
    <v-list lines="two">
      <v-list-subheader>Gast-Zugänge verwalten</v-list-subheader>

      <template
        v-for="([user, groups, guestLink, isBase64, userAvatar], key) in specialUsers"
        :key="key"
      >
        <v-list-item>
          <template v-slot:prepend>
            <div class="mr-4">
              <v-avatar 
                v-if="isBase64" 
                :image="user.avatar" 
                size="40"
              />
              
              <span 
                v-else 
                v-html="userAvatar"
                class="d-flex align-center justify-center"
                style="width: 40px; height: 40px;"
              ></span>
            </div>
          </template>

          <v-list-item-title class="font-weight-bold">
            {{ user.firstName }} {{ user.lastName }}
          </v-list-item-title>

          <v-list-item-subtitle class="mt-2 opacity-100">
            <div class="d-flex flex-wrap align-center ga-2">
              <span class="text-caption text-medium-emphasis">
                Zugriff auf Listen:
              </span>
              
              <v-chip
                v-for="(groupname, innerkey) in groups"
                :key="innerkey"
                color="secondary"
                variant="flat"
                size="small"
                prepend-icon="mdi-gift-outline"
              >
                {{ groupname }}
              </v-chip>
              
              <span v-if="!groups || groups.length === 0" class="text-caption font-italic">
                Keine Listen zugewiesen
              </span>
            </div>
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex align-center">
              <v-tooltip text="Link kopieren" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-content-copy"
                    variant="text"
                    @click="() => copyLinkToClipboard(guestLink as string)"
                  ></v-btn>
                </template>
              </v-tooltip>

              <v-tooltip text="Einladung teilen" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-share-variant"
                    variant="text"
                    class="ml-2"
                    @click="() => shareGuestLink(groups as string[], guestLink as string)"
                  ></v-btn>
                </template>
              </v-tooltip>
            </div>
          </template>
        </v-list-item>
        <v-divider v-if="key !== specialUsers.length - 1" inset></v-divider>
      </template>
    </v-list>
  </v-card>

  <v-snackbar v-model="linkSnackbar" :timeout="5000" color="success">
    {{ snackbarText }}
  </v-snackbar>
</template>

<script setup lang="ts">
import avatar from "animal-avatar-generator";

const userStore = useUserStore();
const giftgroupStore = useGiftGroupStore();
const baseUrl = window.location.origin;

const specialUsers = computed(() =>
  userStore.users
    .filter((user) => user.onlyViewing)
    .map((user) => {
      const guestInformation = userStore.guestInfomrations.find(
        (guestInformation) => guestInformation.email == user.email
      )!;
      
      const link = `${baseUrl}/autologin?user=${guestInformation.email}&password=${guestInformation.password}`;
      const groups = giftgroupStore.giftgroups
        .filter((group) => group.isSpecialUser?.includes(user.email))
        .map((group) => group.name);

      const isBase64 = user.avatar ? user.avatar.split(";").length === 2 : false;
      
      let userAvatar = "";
      if (!isBase64 && user.avatar) {
        userAvatar = avatar(user.avatar, {
          size: 40,
          blackout: false,
        }).replaceAll("\n", "");
      }
      return [user, groups, link, isBase64, userAvatar];
    })
);

onMounted(async () => {
  userStore.loadFromAPI();
  giftgroupStore.loadFromAPI();
  userStore.loadGuestInformation();
});

const linkSnackbar = ref(false);
const snackbarText = ref("");

function copyLinkToClipboard(link: string) {
  navigator.clipboard.writeText(link);
  snackbarText.value = `${link} ins Clipboard kopiert`;
  linkSnackbar.value = true;
}

async function shareGuestLink(groups: string[], link: string) {
  const groupList = groups.map((g) => `- ${g}`).join("\n");

  const messageTitle = "Einladung zu Geschenkelisten";
  const messageText = `Du wurdest eingeladen diese Geschenkelisten zu sehen:\n${groupList}\n\nHiermit bekommst du Zugriff:\n${link}`;

  if (navigator.share) {
    try {
      await navigator.share({
        title: messageTitle,
        text: messageText,
      });
    } catch (err) {
      console.log("Share canceled or failed", err);
    }
  } else {
    navigator.clipboard.writeText(messageText);
    snackbarText.value =
      "Nachricht ins Clipboard kopiert (Teilen nicht verfügbar)";
    linkSnackbar.value = true;
  }
}
</script>