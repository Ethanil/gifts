import { mande, defaults } from "mande";
const api = mande("http://127.0.0.1:5000/api/giftgroups");
export type Giftgroup = {
  id: number;
  editable: boolean;
  isBeingGifted: boolean;
  name: string;
};
export const useGiftGroupStore = defineStore("giftgroups", {
  state: () => ({
    giftgroups: [] as Giftgroup[],
  }),

  actions: {
    async loadFromAPI() {
      try {
        const { token, data } = useAuth();
        defaults.headers.Authorization = String(token.value);
        const response = await api.get({});
        this.giftgroups = response as Giftgroup[];
        // change name of own giftgroup
        if (
          this.giftgroups.length > 0 &&
          this.giftgroups[0].name ==
            `${(data.value as any).firstName} ${
              (data.value as any).lastName
            }'s Liste`
        )
          this.giftgroups[0].name = "Meine Liste";
      } catch (error) {
        console.log(error);
        return error;
      }
    },
  },
  getters: {
    getGiftgroups(state) {
      if (!state.giftgroups) return [];
      return state.giftgroups;
    },
  },
});
