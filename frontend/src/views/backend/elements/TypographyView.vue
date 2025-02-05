<script setup>
import { ref, onMounted, computed} from 'vue';
import axios from 'axios';
import { urlAPI } from '@/main.js';
import Swal from 'sweetalert2';

// State to store the phone details
const phones = ref([]);
const searchQuery = ref('');

// Function to search for a phone
const fetchPhoneDetails = async () => {
  try {
    const response = await axios.get(`${urlAPI}/users`);
    phones.value = response.data["user_data"];
    console.log('Phone details:', response.data["user_data"]);
  } catch (error) {
    console.error('Error fetching phone details:', error);
  }
};

// Call the function to fetch the phone details when the component is mounted
onMounted(() => {
  fetchPhoneDetails();
});

//Computed property to filter the phones
const filteredPhones = computed(() => {
  return phones.value.filter((phone) => {
    return phone.phone.toLowerCase().includes(searchQuery.value.toLowerCase());
  });
});

const selectedPhone = ref(null);
const selectedField = ref('');

const handleButtonClick = (phone, field) => {
  selectedPhone.value = phone;
  selectedField.value = field;
  Swal.fire({
    title: 'Edit:  ' + field,
    html: `
      <input id="fieldValue" class="swal2-input" placeholder="New Value" value="${phone[field]}">
    `,
    focusConfirm: false,
    preConfirm: () => {
      const fieldValue = Swal.getPopup().querySelector('#fieldValue').value;
      if (!fieldValue) {
        Swal.showValidationMessage(`Please enter a value`);
      }
      return { fieldValue: fieldValue };
    }
  }).then((result) => {
    if (result.isConfirmed) {
      updateField(result.value.fieldValue);
    }
  });
};

const handleButtonClickDelete = (phone) => {
  Swal.fire({
    title: 'Are you sure you want to delete this phone?',
    showCancelButton: true,
    confirmButtonText: `Delete`,
  }).then((result) => {
    if (result.isConfirmed) {
      deletePhone(phone);
      };
    }
  );
};

const deletePhone = async (phone) => {
        try {
          const response = await axios.delete(`${urlAPI}/users?phone=${phone.phone}`);
          if(response.status == 200){
            Swal.fire('Success', 'Phone deleted successfully', 'success');
            fetchPhoneDetails();
            // Refresh page
            window.location.reload();
          } else {
            Swal.fire('Error', 'Failed to delete phone', 'error');
          }
        } catch (error) {
          console.error('Error deleting phone:', error);
          Swal.fire('Error', 'Failed to delete phone', 'error');
        }
};
 
const updateField = async (newValue) => {
  if (selectedPhone.value && selectedField.value) {
    try {
      // Make an API call to update the database
      const response = await axios.put(`${urlAPI}/users?phone=${selectedPhone.value.phone}`, {
        [selectedField.value]: newValue, 
      });
      
      // Update the phone value locally
      selectedPhone.value[selectedField.value] = newValue;

      
      if(response.status== 200){
        Swal.fire('Success', 'Phone details updated successfully', 'success');
      } else {
        Swal.fire('Error', 'Failed to update phone details', 'error');
      }
    } catch (error) {
      console.error('Error updating phone details:', error);
      Swal.fire('Error', 'Failed to update phone details', 'error');
    }
  }
};  
</script>

<template>
  <!-- Hero -->
  <BasePageHeading
    title="Active Phones"
    subtitle="Here you can see the data for each phone that has been 
    registered in the system. Use the search bar to filter the results 
    and find the phone you are looking for."
  >
  </BasePageHeading>
  <!-- END Hero -->

  <!-- Search -->
  <div class="content">
    <form @submit.prevent>
      <div class="input-group">
        <input type="text" class="form-control" placeholder="Search by name..."  v-model="searchQuery" @input="search" />
        <span class="input-group-text">
          <i class="fa fa-fw fa-search"></i>
        </span>
      </div>
    </form>
  </div>
  <!-- END Search -->
   
  <!-- Page Content -->
  <div class="content">
    <!-- Headings -->
    <h2 class="content-heading">Phones</h2>
    <div class="row">
      <div class="col-lg-6" v-for="phone in filteredPhones" :key="phone.phone">
        <!-- Bold -->
        <!-- <BaseBlock :title="'Device: ' + phone.phone"> -->
        <BaseBlock >
           <template #title>
            <div class="d-flex justify-content-between align-items-center">
              <span>Device: {{ phone.phone }}</span>
              <button class="btn btn-sm btn-danger"  @click="handleButtonClickDelete(phone)">
                <!-- <i class="si si-note"></i> -->
               <i class="fa fa-times"></i>
              </button>
            </div>
          </template> 
          
          <h5 class="fw-light">Name: <small>{{ phone.phone }}</small>
            <button class="btn btn-edit align-items-right" @click="handleButtonClick(phone, 'phone')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Brand: <small>{{ phone.brand }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'brand')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>

          <h5 class="fw-light">Model: <small>{{ phone.model }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'model')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Color: <small>{{ phone.color }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'color')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Operating System: <small>{{ phone.operating_system }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'operating_system')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>

          <h5 class="fw-light">Serial Number: <small>{{ phone.serial_number }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'serial_number')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Assigned to: <small>{{ phone.assigned_to }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'assigned_to')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Assignee's Name: <small>{{ phone.name }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'name')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Assignee's Email: <small>{{ phone.email }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'email')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Assignee's CDSID: <small>{{ phone.cdsid }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'cdsid')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Assignee's Area Work: <small>{{ phone.area }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'area')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
          
          <h5 class="fw-light">Last Coordinates Registered: <small>{{ phone.last_location }}</small>
            <button class="btn btn-edit" @click="handleButtonClick(phone, 'last_location')">
              <i class="fas fa-edit"></i>
            </button>
          </h5>
    
        </BaseBlock>
      </div>
      </div>  
  </div>
  <!-- END Page Content -->
</template>

<style scoped>
.btn-icon {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  font-size: 1rem; /* Adjust the icon size as needed */
  display: flex;
  align-items: center;
}
/* Puedes agregar estilos adicionales si es necesario */
</style>