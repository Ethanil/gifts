import { h } from "vue";
import type { IconSet, IconProps } from "vuetify";
import MessageLockOffOutline from "./customSVGs/MessageLockOffOutline.vue";
import MessageLockOutline from "./customSVGs/MessageLockOutline.vue";
// import closeIcon from "./customSVGs/close-icon.vue";

const customSvgNameToComponent: any = {
    MessageLockOffOutline,
    MessageLockOutline,
};

const customSVGs: IconSet = {
    component: (props: IconProps) =>
        h(props.tag, [
            h(customSvgNameToComponent[props.icon as string], {
                class: "v-icon__svg",
            }),
        ]),
};

export { customSVGs /* aliases */ };
