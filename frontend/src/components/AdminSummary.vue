<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { authorizedFetch } from '../utils/api';
import AdminNavbar from './AdminNavbar.vue';
import Chart from 'chart.js/auto';

const summary = ref({});
const reservations = ref([]);

// Fetch summary stats from /api/admin/summary
async function loadSummary() {
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/admin/summary');
    if (!res.ok) throw new Error('Failed to load summary');
    summary.value = await res.json();
  } catch (error) {
    console.error('Summary loading failed:', error);
  }
}

// Fetch reservations from /api/admin/history for charts
async function fetchReservations() {
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/admin/history');
    if (res.ok) {
      reservations.value = await res.json();
      await nextTick();
      drawCharts();
    } else {
      console.error(`Failed to fetch admin reservation history: ${res.status}`);
    }
  } catch (err) {
    console.error('Error fetching admin reservations:', err);
  }
}

// Draw revenue & duration charts
function drawCharts() {
  if (window.revenueChart && typeof window.revenueChart.destroy === 'function') window.revenueChart.destroy();
  if (window.durationChart && typeof window.durationChart.destroy === 'function') window.durationChart.destroy();

  const lotData = {};
  reservations.value.forEach(r => {
    const lot = r.lot_name || 'Unknown';
    if (!lotData[lot]) lotData[lot] = { revenue: 0, duration: 0, bookings: 0 };
    lotData[lot].revenue += r.parking_cost || 0;
    if (r.leaving_timestamp) {
      const start = new Date(r.parking_timestamp);
      const end = new Date(r.leaving_timestamp);
      const diffHrs = (end - start) / 3600000;
      lotData[lot].duration += diffHrs;
    }
    lotData[lot].bookings += 1;
  });

  const lots = Object.keys(lotData);
  const revenues = lots.map(l => lotData[l].revenue.toFixed(2));
  const durations = lots.map(l => lotData[l].duration.toFixed(2));

  window.revenueChart = new Chart(
    document.getElementById('revenueChart').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels: lots,
        datasets: [
          {
            label: 'Total Revenue (₹)',
            data: revenues,
            backgroundColor: '#f6c23e'
          }
        ]
      },
      options: {
        plugins: {
          legend: { display: true },
          tooltip: { callbacks: { label: ctx => `₹${ctx.raw}` }}
        },
        scales: {
          x: { title: { display: true, text: 'Parking Lots' }},
          y: { title: { display: true, text: 'Revenue (₹)' }, beginAtZero: true }
        }
      }
    }
  );

  window.durationChart = new Chart(
    document.getElementById('durationChart').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels: lots,
        datasets: [
          {
            label: 'Total Parking Duration (Hours)',
            data: durations,
            backgroundColor: '#36b9cc'
          }
        ]
      },
      options: {
        plugins: {
          legend: { display: true },
          tooltip: { callbacks: { label: ctx => `${ctx.raw} hrs` }}
        },
        scales: {
          x: { title: { display: true, text: 'Parking Lots' }},
          y: { title: { display: true, text: 'Duration (hrs)' }, beginAtZero: true }
        }
      }
    }
  );
}

onMounted(() => {
  loadSummary();
  fetchReservations();
});
</script>

<template>
  <AdminNavbar />
  <div class="container mt-4">
    <div class="text-center mb-4">
      <h2>Admin Summary Dashboard</h2>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card text-center p-3 shadow-sm">
          <h5>Total Parking Lots</h5>
          <p class="fw-bold">{{ summary.total_lots }}</p>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center p-3 shadow-sm">
          <h5>Total Spots</h5>
          <p class="fw-bold">{{ summary.total_spots }}</p>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center p-3 shadow-sm">
          <h5>Occupied Spots</h5>
          <p class="fw-bold text-danger">{{ summary.occupied_spots }}</p>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center p-3 shadow-sm">
          <h5>Available Spots</h5>
          <p class="fw-bold text-success">{{ summary.available_spots }}</p>
        </div>
      </div>
    </div>

    <div class="alert alert-info mb-4">Summary charts with parking lot revenue and usage stats below.</div>

    <!-- Charts -->
    <canvas id="revenueChart"></canvas>
    <canvas id="durationChart" class="mt-5"></canvas>
  </div>
</template>