import { mande } from 'mande'
//http://0.0.0.0
const api = mande('http://127.0.0.1:5000/api/items')
export type Item = {
  "id": Number,
  "description": String,
  "name": String,
  "rank": String
  "price": Number,
  "timestamp": Date
}
export type JSONReturn = {
  items: Item[]
};
export const useMyItemsStore = defineStore('myItems', {
  state: () => ({
    items: [] as Item[],
  }),

  actions: {
    async loadFromAPI() {
      try {
        const response = await api.get({})
        this.items = response
      } catch (error) {
        console.log(error)
        return error
      }
    },
  },
})