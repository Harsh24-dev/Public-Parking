<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { authorizedFetch } from '../utils/api';
import UserNavbar from './UserNavbar.vue';
import Chart from 'chart.js/auto';

const reservations = ref([]);
const message = ref('');
const statusClass = ref('');

async function fetchReservations() {
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/user/history');
    if (res.ok) {
      reservations.value = await res.json();
      await nextTick();
      drawCharts();
    } else {
      console.error(`Failed to fetch reservations: ${res.status}`);
    }
  } catch (err) {
    console.error('Error fetching reservations:', err);
  }
}

function drawCharts() {
  if (window.durationChart?.destroy) window.durationChart.destroy();
  if (window.locationChart?.destroy) window.locationChart.destroy();

 
  const durationLabels = reservations.value.map((r, i) => `Booking ${i + 1}`);
  const durations = reservations.value.map(r => {
    if (!r.leaving_timestamp) return 0;
    const start = new Date(r.parking_timestamp);
    const end = new Date(r.leaving_timestamp);
    return Math.round(((end - start) / 3600000) * 100) / 100;
  });

  window.durationChart = new Chart(
    document.getElementById('durationChart').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels: durationLabels,
        datasets: [
          {
            label: 'Parking Duration (Hours)',
            data: durations,
            backgroundColor: '#1cc88a'
          }
        ]
      },
      options: {
        plugins: {
          legend: { display: true },
          tooltip: { callbacks: { label: ctx => `${ctx.raw} hrs` }}
        },
        scales: {
          x: { title: { display: true, text: 'Bookings' }},
          y: { title: { display: true, text: 'Hours' }, beginAtZero: true }
        }
      }
    }
  );

  const locationCounts = {};
  reservations.value.forEach(r => {
    const lotName = r.lot_name || 'Unknown';
    locationCounts[lotName] = (locationCounts[lotName] || 0) + 1;
  });

  const locationLabels = Object.keys(locationCounts);
  const locationData = Object.values(locationCounts);

  window.locationChart = new Chart(
    document.getElementById('locationChart').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels: locationLabels,
        datasets: [
          {
            label: 'Number of Bookings per Location',
            data: locationData,
            backgroundColor: '#36b9cc'
          }
        ]
      },
      options: {
        plugins: {
          legend: { display: true },
          tooltip: { callbacks: { label: ctx => `${ctx.raw} bookings` }}
        },
        scales: {
          x: { title: { display: true, text: 'Parking Location' }},
          y: { title: { display: true, text: 'Number of Bookings' }, beginAtZero: true }
        }
      }
    }
  );
}

async function exportCSV() {
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/user/export', {
      method: 'POST',
    });

    const data = await res.json();
    if (res.ok) {
      message.value = 'Export job started! Check your email shortly.';
      statusClass.value = 'alert alert-success';
    } else {
      message.value = `Failed: ${data.error || data.message}`;
      statusClass.value = 'alert alert-danger';
    }
  } catch (err) {
    message.value = 'An unexpected error occurred.';
    statusClass.value = 'alert alert-danger';
    console.error(err);
  }
}

onMounted(fetchReservations);
</script>


<template>
  <UserNavbar />
  <div class="container mt-4">
    <h3 class="text-center mb-4">Parking Summary</h3>

    <!-- 📊 Charts -->
    <canvas id="durationChart"></canvas>
    <canvas id="locationChart" class="mt-5"></canvas>

    <!-- 📤 Export CSV Button -->
    <div class="text-center mt-5">
      <button @click="exportCSV" class="btn btn-primary">
        Export Parking History as CSV
      </button>
      <div v-if="message" class="mt-3 alert" :class="statusClass">
        {{ message }}
      </div>
    </div>
  </div>
</template>