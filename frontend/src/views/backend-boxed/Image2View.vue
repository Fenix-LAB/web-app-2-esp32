<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import axios from 'axios';
import { urlAPI } from '@/main.js';

const center = ref([-99.28868264962121, 19.525565555281677]); // GTBC

const projection = ref("EPSG:4326");
const zoom = ref(15);
const offset = ref(0);
const responseData = ref([{}]); // Propiedad para almacenar la respuesta

function moveToEast() {
  offset.value += 0.1;
}

// Función para realizar la solicitud a la API
const fetchData = () => {
  axios.get(`${urlAPI}/phone_data`)
    .then(response => {
      console.log(response.data);
      responseData.value = response.data; // Almacena la respuesta en el estado
    })
    .catch(error => {
      console.log(error);
    });
};

// Request to the backend API cada 30 segundos
onMounted(() => {
  fetchData(); // Llama a la API inmediatamente al montar el componente
  const interval = setInterval(fetchData, 60000); // Llama a la API cada 30 segundos

  // Limpia el intervalo cuando el componente se desmonta
  onUnmounted(() => {
    clearInterval(interval);
  });
});
</script>

<template>
  <!-- Hero -->
  <BaseBackground
    style="height: 170px"
    image="/assets/media/photos/auto3.jpg"
  >
    <div class="py-4 text-center">
      <h1 class="fw-semibold">
        Ford
        <h3>Sentinel</h3>
      </h1>
    </div>
  </BaseBackground>
  <!-- END Hero -->

  <!-- Page Content -->
  <div class="content">
    <div class="col-12">
      <BaseBlock>
        <big>
          <b>Phone Location</b>
        </big>
        <ol-map style="height: 600px">
          <ol-view
            ref="view"
            :center="center"
            :zoom="zoom"
            :projection="projection"
          />

          <ol-tile-layer>
            <ol-source-osm />
          </ol-tile-layer>

          <ol-overlay
            v-for="obj in responseData.phone_data"
            :key="obj.name"
            :position="[obj.longitude, obj.latitude]"
            :autoPan="true"
          >
            <div class="overlay-content">
              <span class="si si-phone"></span>
              {{ obj.name }}
            </div>
          </ol-overlay>
        </ol-map>
      </BaseBlock>
    </div>
  </div>
  <!-- END Page Content -->
</template>

<style scoped> 
.overlay-content {
  background: transparent;
  /* box-shadow: 0 5px 10px rgb(2 2 2 / 20%); */
  padding: 10px 20px;
  font-size: 16px;
  color: #000;
}
</style>