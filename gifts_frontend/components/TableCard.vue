<template>
    <v-card>
        <v-card-title>{{ title }}</v-card-title>
        <v-data-table :items="items"></v-data-table>
    </v-card>
</template>
<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    items: {
      type: Array,
      required: true,
    },
  }
};
</script>