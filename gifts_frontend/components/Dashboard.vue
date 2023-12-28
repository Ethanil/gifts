<template>
  <v-container>
    <v-row>
      <v-col>
        <TableCard
          :items="myItemsStore.items"
          :title="'Meine Geschenke'"
        ></TableCard>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <TableCard
          :items="peopleForShoppingFor"
          :title="'People I\'m shopping for'"
        ></TableCard>
      </v-col>
      <v-col> People I'm not shopping for </v-col>
    </v-row>
    <v-row>
      <v-col> Messages </v-col>
      <v-col> Upcoming events </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
import {useMyItemsStore} from '@/stores/myItemStore';
const myItemsStore = useMyItemsStore();
await myItemsStore.loadFromAPI();
const peopleForShoppingFor = [
  {
    Name: "test",
    LastUpdated: "gestern",
    "#Items": "4",
    Actions: "",
  },
];
</script>
