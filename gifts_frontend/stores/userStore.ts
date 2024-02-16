import { mande, defaults } from "mande";
const api = mande("http://127.0.0.1:5000/api/users");
export type User = {
  email: string;
  firstName: string;
  lastName: string;
  avatar: File | string;
};
export const useUserStore = defineStore("user", {
  state: () => ({
    users: [] as User[],
  }),

  actions: {
    async loadFromAPI() {
      try {
        const { token, data } = useAuth();
        defaults.headers.Authorization = String(token.value);
        const response = await api.get();
        this.users = response as User[];
        // change name of own giftgroup
      } catch (error) {
        console.log(error);
        return error;
      }
    },
  },
});
