import { createRouter, createWebHashHistory } from "vue-router";

import NProgress from "nprogress/nprogress.js";

// Main layouts
import LayoutBackend from "@/layouts/variations/BackendStarter.vue";
import LayoutSimple from "@/layouts/variations/Simple.vue";

// Auth: Login
const AuthSignIn3 = () => import("@/views/auth/SignIn3View.vue");
const AuthSignUp3 = () => import("@/views/auth/SignUp3View.vue");
const AuthReminder3 = () => import("@/views/auth/Reminder3View.vue");

// Pages: Profile
const BackendPagesGenericProfile = () =>
  import("@/views/backend/pages/generic/ProfileView.vue");

// Dashboard: Map
const BackendBoxedImage2 = () => import("@/views/backend-boxed/Image2View.vue");

// Frontend: Landing
const Landing = () => import("@/views/starter/LandingView.vue");

// Backend: Dashboard
const Dashboard = () => import("@/views/starter/DashboardView.vue");
const BackendBlocksForms = () => import("@/views/backend/blocks/FormsView.vue");
const BackendElementsTypography = () =>
  import("@/views/backend/elements/TypographyView.vue");
const BackendFormsValidation = () => import("@/views/backend/forms/ValidationView.vue");
const BackendPagesGenericSearch = () =>
  import("@/views/backend/pages/generic/SearchView.vue");
// Set all routes
const routes = [
  /*
  |
  |--------------------------------------------------------------------------
  | Auth Routes
  |--------------------------------------------------------------------------
  |
  */
  {
    path: "/",
    component: LayoutSimple,
    children: [
      {
        path: "",
        name: "auth-signin3",
        component: AuthSignIn3,
      },
      {
        path: "signup3",
        name: "auth-signup3",
        component: AuthSignUp3,
      },
      {
        path: "reminder3",
        name: "auth-reminder3",
        component: AuthReminder3,
      },
    ],
  },

  /*
  |
  |--------------------------------------------------------------------------
  | Landing Routes
  |--------------------------------------------------------------------------
  |
  */
  // {
  //   path: "/landing",
  //   component: LayoutSimple,
  //   children: [
  //     {
  //       path: "",
  //       name: "landing",
  //       component: Landing,
  //     },
  //   ],
  // },
  /*
  |
  |--------------------------------------------------------------------------
  | Backend Routes
  |--------------------------------------------------------------------------
  |
  */
  {
    path: "/backend",
    // redirect: "/backend/dashboard",
    component: LayoutBackend,
    children: [
      // {
      //   path: "dashboard",
      //   name: "backend-dashboard",
      //   component: Dashboard,
      // },
      /*
      |
      |--------------------------------------------------------------------------
      | Profile
      |--------------------------------------------------------------------------
      |
      */
      {
        path: "/map",
        redirect: "/pages/generic/blank",
        children: [
          {
            path: "",
            name: "backend-boxed-image2",
            component: BackendBoxedImage2,
          },
        ],
      },
      {
        path: "/register",
        redirect: "/pages/generic/blank",
        children: [
          {
            path: "",
            name: "backend-form-validation",
            component: BackendFormsValidation,
          },
        ],
      },
      {
        path: "/details",
        redirect: "/pages/generic/blank",
        children: [
          {
            path: "",
            name: "backend-elements-typography",
            component: BackendElementsTypography,
          },
        ],
      },
      {
        path: "/history",
        redirect: "/pages/generic/blank",
        children: [
          {
            path: "",
            name: "backend-pages-generic-search",
            component: BackendPagesGenericSearch,
          },
        ],
      },

    ],
  },
];

// Create Router
const router = createRouter({
  history: createWebHashHistory(),
  linkActiveClass: "active",
  linkExactActiveClass: "active",
  scrollBehavior() {
    return { left: 0, top: 0 };
  },
  routes,
});


// NProgress
/*eslint-disable no-unused-vars*/
NProgress.configure({ showSpinner: false });

router.beforeResolve((to, from, next) => {
  NProgress.start();
  next();
});

router.afterEach((to, from) => {
  NProgress.done();
});
/*eslint-enable no-unused-vars*/

export default router;
