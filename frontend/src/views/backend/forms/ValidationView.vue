<script setup>
import { reactive, computed } from "vue";
import axios from 'axios';
import Swal from 'sweetalert2';
import { urlAPI } from '@/main.js';

// Vuelidate, for more info and examples you can check out https://github.com/vuelidate/vuelidate
import useVuelidate from "@vuelidate/core";
import {
  required,
  minLength,
  between,
  email,
  decimal,
  integer,
  url,
  sameAs,
} from "@vuelidate/validators";

// Initial State
const initialState = {
  phone: null,
  brand: null,
  model: null,
  color: null,
  operating_system: null,
  serial_number: null,
  assigned_to: null,
  name: null,
  email: null,
  cdsid: null,
  area: null,
  terms: false,
};



// Example options for select
const options = reactive([
  { value: null, text: "Please select" },
  { value: "html", text: "HTML" },
  { value: "css", text: "CSS" },
  { value: "javascript", text: "JavaScript" },
  { value: "angular", text: "Angular" },
  { value: "react", text: "React" },
  { value: "vuejs", text: "Vue.js" },
  { value: "ruby", text: "Ruby" },
  { value: "php", text: "PHP" },
  { value: "asp", text: "ASP.NET" },
  { value: "python", text: "Python" },
  { value: "mysql", text: "MySQL" },
]);

// Input state variables
const state = reactive({ ...initialState
  // phone: null,
  // brand: null,
  // model: null,
  // color: null,
  // operating_system: null,
  // serial_number: null,
  // assigned_to: null,
  // name: null,
  // email: null,
  // cdsid: null,
  // area: null,
  // terms: null,
});

// Validation rules
const rules = computed(() => {
  return {
    phone: {
      required,
      minLength: minLength(3),
    },
    brand: {
      required,
      minLength: minLength(3),
    },
    model: {
      required,
      minLength: minLength(3),
    },
    color: {
      required,
      minLength: minLength(3),
    },
    operating_system: {
      required,
      minLength: minLength(3),
    },
    serial_number: {
      required,
      minLength: minLength(3),
    },
    assigned_to: {
      required,
      minLength: minLength(3),
    },
    name: {
      required,
      minLength: minLength(3),
    },
    email: {
      required,
      minLength: minLength(3),
    },
    cdsid: {
      required,
      minLength: minLength(3),
    },
    area: {
      required,
      minLength: minLength(3),
    },
    terms: {
      required,
      sameAs: sameAs(true),
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
        console.log('Form is invalid');
        return;
      }

      // perform async actions
      console.log('Data: ', state);
      
      try {
        var code_status = 0;
        const response = await axios.post(`${urlAPI}/users`, state);
        console.log('Response:', response.data);
        console.log('status code:', response.status);
        code_status = response.status;

        // notify user form was submitted
        if (code_status === 200) {
          console.log('Phone registered successfully');
          Swal.fire({
          title: 'Registered!',
          text: 'Your information has been successfully registered.',
          icon: 'success',
          confirmButtonText: 'OK'
        });}
        else {
          console.log('Error registering phone');
          Swal.fire({
          title: 'Error!',
          text: 'There was an error registering your information, please try again.',
          icon: 'error',
          confirmButtonText: 'OK'
        });
        }        
      } catch (error) {
        console.error('Error:', error);
        Swal.fire({
          title: 'Error!',
          text: 'There was an error registering your information, please try again.',
          icon: 'error',
          confirmButtonText: 'OK'
        });
      }

      // reset form
      Object.assign(state, initialState);
      v$.value.$reset();

    return {
      state,
      v$,
      onSubmit
    }
};
</script>

<template>
  <!-- Hero -->
  <BasePageHeading
    title="Phone Registration"
    subtitle="You are now ready to register a new phone."
  >
  </BasePageHeading>
  <!-- END Hero -->

  <!-- Page Content -->
  <div class="content">
    <form @submit.prevent="onSubmit">
      <BaseBlock title="New Phone" content-full>
        <!-- Regular -->
        <h2 class="content-heading border-bottom mb-4 pb-2">About phone</h2>
        <div class="row items-push">
          <div class="col-lg-4">
            <p class="fs-sm text-muted">
              Phone name, brand, model, color, operating system, serial number, assigned to.
            </p>
          </div>
          <div class="col-lg-8 col-xl-5">
            <div class="mb-4">
              <label class="form-label" for="val-phone"
                >Phone Name<span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-phone"
                class="form-control"
                :class="{
                  'is-invalid': v$.phone.$errors.length,
                }"
                v-model="state.phone"
                @blur="v$.phone.$touch"
                placeholder="Enter phone name.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-brand"
                >Brand <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-brand"
                class="form-control"
                :class="{
                  'is-invalid': v$.brand.$errors.length,
                }"
                v-model="state.brand"
                @blur="v$.brand.$touch"
                placeholder="Enter phone brand.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-model"
                >Model <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-model"
                class="form-control"
                :class="{
                  'is-invalid': v$.model.$errors.length,
                }"
                v-model="state.model"
                @blur="v$.model.$touch"
                placeholder="Enter phone model.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-color"
                >Color <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-color"
                class="form-control"
                :class="{
                  'is-invalid': v$.color.$errors.length,
                }"
                v-model="state.color"
                @blur="v$.color.$touch"
                placeholder="Enter phone color.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-operating-system"
                >Operating System <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-operating-system"
                class="form-control"
                :class="{
                  'is-invalid': v$.operating_system.$errors.length,
                }"
                v-model="state.operating_system"
                @blur="v$.operating_system.$touch"
                placeholder="Enter operating system.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-serial-number"
                >Serial Number <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-serial-number"
                class="form-control"
                :class="{
                  'is-invalid': v$.serial_number.$errors.length,
                }"
                v-model="state.serial_number"
                @blur="v$.serial_number.$touch"
                placeholder="Enter serial number.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-assigned-to"
                >Assigned to <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-assigned-to"
                class="form-control"
                :class="{
                  'is-invalid': v$.assigned_to.$errors.length,
                }"
                v-model="state.assigned_to"
                @blur="v$.assigned_to.$touch"
                placeholder="Enter name and last name.."
              />
            </div>
          </div>
        </div>
        <!-- END Regular -->

        <!-- Advanced -->
        <h2 class="content-heading border-bottom mb-4 pb-2">Assignee info</h2>
        <div class="row items-push">
          <div class="col-lg-4">
            <p class="fs-sm text-muted">
              It's important to enter the information of the person responsible 
              for the phone to facilitate management and communication if necessary.
            </p>
          </div>
          <div class="col-lg-8 col-xl-5">
            <div class="mb-4">
              <label class="form-label" for="val-name"
                >Name <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-name"
                class="form-control"
                :class="{
                  'is-invalid': v$.name.$errors.length,
                }"
                v-model="state.name"
                @blur="v$.name.$touch"
                placeholder="Enter name and last name.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-email"
                >Email <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-email"
                class="form-control"
                :class="{
                  'is-invalid': v$.email.$errors.length,
                }"
                v-model="state.email"
                @blur="v$.email.$touch"
                placeholder="Enter ford email.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-cdsid"
                >CDSID <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-cdsid"
                class="form-control"
                :class="{
                  'is-invalid': v$.cdsid.$errors.length,
                }"
                v-model="state.cdsid"
                @blur="v$.cdsid.$touch"
                placeholder="Enter CDSID.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label" for="val-area"
                >Area <span class="text-danger">*</span></label
              >
              <input
                type="text"
                id="val-area"
                class="form-control"
                :class="{
                  'is-invalid': v$.area.$errors.length,
                }"
                v-model="state.area"
                @blur="v$.area.$touch"
                placeholder="Enter area or team work.."
              />
            </div>
            <div class="mb-4">
              <label class="form-label">Terms &amp; Conditions</label>
              <span class="text-danger">*</span>
              <div
                class="form-check"
                :class="{
                  'is-invalid': v$.terms.$errors.length,
                }"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="val-terms"
                  :class="{
                    'is-invalid': v$.terms.$errors.length,
                  }"
                  v-model="state.terms"
                  @blur="v$.terms.$touch"
                />
                <label class="form-check-label" for="val-terms">I agree</label>
              </div>
              <div
                v-if="v$.terms.$errors.length"
                class="invalid-feedback animated fadeIn"
              >
                You must agree to the service terms!
              </div>
            </div>
          </div>
        </div>
        <!-- END Advanced -->

        <!-- Submit -->
        <div class="row items-push">
          <div class="col-lg-7 offset-lg-4">
            <button type="submit" class="btn btn-alt-primary">Submit</button>
          </div>
        </div>
        <!-- END Submit -->

      </BaseBlock>
    </form>
  </div>
  <!-- END Page Content -->

</template>
