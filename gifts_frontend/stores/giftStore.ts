import { mande, defaults } from "mande";
const api = mande("http://127.0.0.1:5000/api/gifts");
export type Gift = {
  name: string;
  price: number;
  giftStrength: number;
  description: string;
  link: string;
  picture: Blob | string;
  availableActions: string[];
};
export type DatabaseGift = Gift & {
  id: number;
  giftGroup_id: number;
  user_email: string;
};
export enum GiftStrength {
  'Ganz okay' = 1,
  'Okay' = 2,
  'Gut' = 3,
  'Super' = 4,
  'Mega' = 5,
}
enum BackendGiftStrength {
  OKAY = 1,
  GOOD = 2,
  GREAT = 3,
  AMAZING = 4,
  AWESOME = 5,
}
export const useGiftStore = defineStore("gift", {
  state: () => ({
    gifts: {} as { [key: number]: DatabaseGift[] },
    groupId: 0 as number,
  }),

  actions: {
    async loadFromAPI() {
      try {
        const { token } = useAuth();
        defaults.headers.Authorization = String(token.value);
        const response = await api.get();
        this.gifts = response as { [key: number]: DatabaseGift[] };
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    setGroup(giftGroup_id: number) {
      this.groupId = giftGroup_id;
    },
    async addGift(gift: Gift) {
      const formData = new FormData();
      for (let [key, value] of Object.entries(gift)) {
        switch (typeof value) {
          case "number":
            if( key === "giftStrength") formData.append(key, BackendGiftStrength[value]);
            else formData.append(key, value.toString());
            break;
          case "string":
            formData.append(key, value);
            break;
          default:
            if (key !== "availableActions") formData.append(key, value as Blob);
            break;
        }
      }
      try {
        const { token } = useAuth();
        defaults.headers.Authorization = String(token.value);
        const response = await fetch(
          "http://127.0.0.1:5000/api/gifts/" + this.groupId,
          {
            method: "POST",
            body: formData,
            headers: {
              Authorization: token.value!,
            },
          }
        );
      } catch (error) {
        console.log(error);
        return error;
      } finally {
        this.loadFromAPI();
      }
    },
    async reserveGift(gift: DatabaseGift, giftGroup: Giftgroup) {
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?reserve=true`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    async stopReserveGift(gift: DatabaseGift, giftGroup: Giftgroup) {
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?reserve=true`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    async freeReserveGift(gift: DatabaseGift, giftGroup: Giftgroup) {
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?reserve=true`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    async stopFreeReserveGift(gift: DatabaseGift, giftGroup: Giftgroup) {
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?reserve=true`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    async requestFreeReserveGift(gift: DatabaseGift, giftGroup: Giftgroup) {
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?reserve=true`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
    async doAction(
      gift: DatabaseGift,
      giftGroup: Giftgroup,
      queryParams: {
        reserve?: boolean;
        freeReserve?: boolean;
        requestFreeReserve?: boolean;
      }
    ) {
      let queryString = "";
      if (queryParams.reserve !== undefined)
        queryString += "reserve=" + queryParams.reserve;
      if (queryParams.freeReserve !== undefined) {
        queryString += queryString !== "" ? "?" : "";
        queryString += "free_reserve=" + queryParams.freeReserve;
      }
      if (queryParams.requestFreeReserve !== undefined) {
        queryString += queryString !== "" ? "?" : "";
        queryString += "request_free_reserve=" + queryParams.requestFreeReserve;
      }
      try {
        const response = await api.patch(
          `/${giftGroup.id}/${gift.id}?${queryString}`
        );
      } catch (error) {
        console.log(error);
        return error;
      }
    },
  },
  getters: {
    getGiftsOfCurrentGroup(state): DatabaseGift[] {
      if (!state.gifts || !state.gifts[state.groupId]) return [];
      return state.gifts[state.groupId];
    },
  },
});
