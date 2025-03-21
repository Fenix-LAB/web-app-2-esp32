<script setup>
import { reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { useTemplateStore } from "@/stores/template";

// Vuelidate, for more info and examples you can check out https://github.com/vuelidate/vuelidate
import useVuelidate from "@vuelidate/core";
import { required, minLength } from "@vuelidate/validators";

// Main store and Router
const store = useTemplateStore();
const router = useRouter();

// Input state variables
const state = reactive({
  username: null,
  password: null,
});

// Validation rules
const rules = computed(() => {
  return {
    username: {
      required,
      minLength: minLength(3),
    },
    password: {
      required,
      minLength: minLength(5),
    },
  };
});

// Use vuelidate
const v$ = useVuelidate(rules, state);

// On form submission
async function onSubmit() {
  const result = await v$.value.$validate();

  if (!result) {
    // notify user form is invalid
    return;
  }

  // Validate user credentials
  // If valid, store user data in local storage
  // and redirect to profile page
  console.log("User data", state);
  const data_user = JSON.stringify(state)
  console.log("User data", data_user);
  if (state.username !== "admin" || state.password !== "admin") {
    alert("Invalid credentials");
    return;
  }
  localStorage.setItem("user", JSON.stringify(state));
  localStorage.setItem("isAuthenticated", true);
  // Go to dashboard
  router.push({ name: "backend-dashboard"});
}
</script>
<style scoped>
.large-text {
  font-size: 3rem; /* Ajusta el tamaño según tus necesidades */
  font-weight: bold; /* Opcional: para hacer el texto más grueso */
}
</style>

<template>
  <!-- Page Content -->
  <BaseBackground 
  
  image="/assets/media/photos/photo36@2x.jpg">
    
    <div class="row g-0 bg-primary-dark-op">
      <!-- Meta Info Section -->
      <div
        
        class="hero-static col-lg-3 d-none d-lg-flex flex-column justify-content-center"
      >
        <div class="p-1 p-xl-7 flex-grow-2 d-flex align-items-center">
          <div class="w-100">
            <!-- <img src="frontend\public\assets\media\photos\ford1.jpg" alt="Descripción de la imagen" width="300" height="200"> -->
            <!-- <img src="frontend\public\assets\media\photos\ford1.jpg" > -->
            <!-- <RouterLink
              :to="{ name: 'landing' }"
              class="link-fx fw-semibold fs-2 text-white"
            >
              One<span class="fw-normal">UI</span>
            </RouterLink> -->
            <p class="text-white-300 me-xl.8 mt-10 large-text">
              Welcome to APP NAME!
            </p>
          </div>
        </div>
        <div
          class="p-4 p-xl-5 d-xl-flex justify-content-between align-items-center fs-sm"
        >
          <p class="fw-medium text-white-50 mb-0">
            <strong>{{ store.app.name + " " + store.app.version }}</strong>
            &copy; {{ store.app.copyright }}
          </p>
          <ul class="list list-inline mb-0 py-2">
            <li class="list-inline-item">
              <a class="text-white-75 fw-medium" href="javascript:void(0)"
                >Legal</a
              >
            </li>
            <li class="list-inline-item">
              <a class="text-white-75 fw-medium" href="javascript:void(0)"
                >Contact</a 
              >
            </li>
            <li class="list-inline-item">
              <a class="text-white-75 fw-medium" href="javascript:void(0)"
                >Terms</a
              >
            </li>
          </ul>
        </div>
      </div>
      <!-- END Meta Info Section -->

      <!-- Main Section -->
      <div
        class="hero-static col-lg-7 d-flex flex-column align-items-center bg-body-extra-light"
      >
        <div class="p-2 w-100 d-lg-none text-center">
          <!-- <RouterLink
            :to="{ name: 'landing' }"
            class="link-fx fw-semibold fs-3 text-dark"
          >
            One<span class="fw-normal">UI</span>
          </RouterLink> -->
        </div>
        <div class="p-8 w-100 flex-grow-1 d-flex align-items-center">
          <div class="w-100">
            <!-- Header -->
            <div class="text-center mb-5">
              <p class="mb-3">
                <i class="fa fa-2x fa-circle-notch text-primary-light"></i>
              </p>
              <h1 class="fw-bold mb-2">Sign In</h1>
              <p class="fw-medium text-muted">
                Welcome, please login or
                <RouterLink :to="{ name: 'auth-signup3' }">sign up</RouterLink>
                for a new account.
              </p>
            </div>
            <!-- END Header -->

            <!-- Sign In Form -->
            <div 
            
            class="row g-0 justify-content-center">
              <div class="col-sm-8 col-xl-4">
                <form @submit.prevent="onSubmit">
                  <div class="mb-4">
                    <input
                      type="text"
                      class="form-control form-control-lg form-control-alt py-3"
                      id="login-username"
                      name="login-username"
                      placeholder="Username"
                      :class="{
                        'is-invalid': v$.username.$errors.length,
                      }"
                      v-model="state.username"
                      @blur="v$.username.$touch"
                    />
                    <div
                      v-if="v$.username.$errors.length"
                      class="invalid-feedback animated fadeIn"
                    >
                      Please enter your username
                    </div>
                  </div>
                  <div class="mb-4">
                    <input
                      type="password"
                      class="form-control form-control-lg form-control-alt py-3"
                      id="login-password"
                      name="login-password"
                      placeholder="Password"
                      :class="{
                        'is-invalid': v$.password.$errors.length,
                      }"
                      v-model="state.password"
                      @blur="v$.password.$touch"
                    />
                    <div
                      v-if="v$.password.$errors.length"
                      class="invalid-feedback animated fadeIn"
                    >
                      Please enter your password
                    </div>
                  </div>
                  <div
                    class="d-flex justify-content-between align-items-center mb-4"
                  >
                    <div>
                      <RouterLink
                        :to="{ name: 'auth-reminder3' }"
                        class="text-muted fs-sm fw-medium d-block d-lg-inline-block mb-1"
                      >
                        Forgot Password?
                      </RouterLink>
                    </div>
                    <div>
                      <button type="submit" class="btn btn-lg btn-alt-primary">
                        <i class="fa fa-fw fa-sign-in-alt me-1 opacity-50"></i>
                        Sign In
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
            <!-- END Sign In Form -->
          </div>
        </div>
        <div
          class="px-4 py-3 w-100 d-lg-none d-flex flex-column flex-sm-row justify-content-between fs-sm text-center text-sm-start"
        >
          <p class="fw-medium text-black-50 py-2 mb-0">
            <strong>{{ store.app.name + " " + store.app.version }}</strong>
            &copy; {{ store.app.copyright }}
          </p>
          <ul class="list list-inline py-2 mb-0">
            <li class="list-inline-item">
              <a class="text-muted fw-medium" href="javascript:void(0)"
                >Legal</a
              >
            </li>
            <li class="list-inline-item">
              <a class="text-muted fw-medium" href="javascript:void(0)"
                >Contact</a
              >
            </li>
            <li class="list-inline-item">
              <a class="text-muted fw-medium" href="javascript:void(0)"
                >Terms</a
              >
            </li>
          </ul>
        </div>
      </div>
      <!-- END Main Section -->
    </div>
  </BaseBackground>
  <!-- END Page Content -->
</template>
