import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";

// You can use the following starter router instead of the default one as a clean starting point
// import router from "./router/starter";
import router from "./router/starter";

// Template components
import BaseBlock from "@/components/BaseBlock.vue";
import BaseBackground from "@/components/BaseBackground.vue";
import BasePageHeading from "@/components/BasePageHeading.vue";

// Template directives
import clickRipple from "@/directives/clickRipple";

// Bootstrap framework
import * as bootstrap from "bootstrap";
window.bootstrap = bootstrap;

// Maps
import "vue3-openlayers/styles.css";
import OpenLayersMap from "vue3-openlayers";

// Craft new application
const app = createApp(App);

//Base url API
export const urlAPI = "https://jidknyggjx.us-east-1.awsapprunner.com/api/v1";


// Register global components
app.component("BaseBlock", BaseBlock);
app.component("BaseBackground", BaseBackground);
app.component("BasePageHeading", BasePageHeading);

// Register global directives
app.directive("click-ripple", clickRipple);

// Use Pinia and Vue Router
app.use(createPinia());
app.use(router);
app.use(OpenLayersMap /*, options */);

// ..and finally mount it!
app.mount("#app");
