<template>
  <NuxtLayout>
    <v-app>
      <TopToolbar></TopToolbar>
      <v-main>
        <NuxtPage />
      </v-main>
    </v-app>
  </NuxtLayout>
</template>

<script lang="ts" setup>
import { useTheme } from "vuetify";

const theme = useTheme();
onMounted(() => {
  const selectedTheme = localStorage.getItem("selectedTheme");
  if (selectedTheme) {
    theme.global.name.value = selectedTheme;
  } else {
    localStorage.setItem("selectedTheme", "light");
  }
});
function toggleTheme() {
  const selectedTheme = theme.global.current.value.dark ? "light" : "dark";
  localStorage.setItem("selectedTheme", selectedTheme);
  theme.global.name.value = selectedTheme;
}

const menuOptions = [
  {
    label: "Hear the Wind Sing",
    key: "hear-the-wind-sing",
  },
  {
    label: "Pinball 1973",
    key: "pinball-1973",
    disabled: true,
    children: [
      {
        label: "Rat",
        key: "rat",
      },
    ],
  },
  {
    label: "A Wild Sheep Chase",
    key: "a-wild-sheep-chase",
    disabled: true,
  },
  {
    label: "Dance Dance Dance",
    key: "Dance Dance Dance",
    children: [
      {
        type: "group",
        label: "People",
        key: "people",
        children: [
          {
            label: "Narrator",
            key: "narrator",
          },
          {
            label: "Sheep Man",
            key: "sheep-man",
          },
        ],
      },
      {
        label: "Beverage",
        key: "beverage",
        children: [
          {
            label: "Whisky",
            key: "whisky",
          },
        ],
      },
      {
        label: "Food",
        key: "food",
        children: [
          {
            label: "Sandwich",
            key: "sandwich",
          },
        ],
      },
      {
        label: "The past increases. The future recedes.",
        key: "the-past-increases-the-future-recedes",
      },
    ],
  },
];
</script>
<style lang="scss">
// body {
//   color: #f5f5f5;
//   background-color: #202124;
// }
</style>
