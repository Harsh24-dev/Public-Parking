<script setup>
import { ref, computed, onMounted } from 'vue';
import { authorizedFetch } from '../utils/api';
import UserNavbar from './UserNavbar.vue';

const reservations = ref([]);
const historyError = ref('');
const loadingHistory = ref(true);

async function fetchReservations() {
  historyError.value = '';
  loadingHistory.value = true;
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/user/history');
    if (res.ok) {
      reservations.value = await res.json();
    } else {
      historyError.value = `Failed to load reservation history (${res.status})`;
    }
  } catch (err) {
    historyError.value = 'Error loading reservation history.';
    console.error(err);
  } finally {
    loadingHistory.value = false;
  }
}

async function releaseParking(reservationId) {
  if (!confirm('Are you sure you want to release this spot?')) return;
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/user/release/${reservationId}`, {
      method: 'POST'
    });
    if (res.ok) {
      const data = await res.json();
      alert(`Spot released! Total cost: ₹${data.cost}`);
      await fetchReservations();
    } else {
      const err = await res.json();
      alert(err.error || 'Release failed.');
    }
  } catch (err) {
    console.error(err);
    alert('Something went wrong during release.');
  }
}

async function bookSpot(lotId) {
  if (!confirm('Are you sure you want to rebook this lot?')) return;
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/user/book/${lotId}`, {
      method: 'POST'
    });
    if (res.ok) {
      const data = await res.json();
      alert(`Booking successful! Reservation ID: ${data.Reservation_id}`);
      await fetchReservations();
    } else {
      const err = await res.json();
      alert(err.error || 'Failed to rebook a spot.');
    }
  } catch (err) {
    console.error('Booking error:', err);
  }
}

function formatDate(dateStr) {
  return dateStr ? new Date(dateStr).toLocaleString() : '';
}

const activeReservations = computed(() => reservations.value.filter(r => r.status === 'active'));

onMounted(fetchReservations);
</script>

<template>
  <UserNavbar/>
  <table v-if="!loadingHistory && reservations.length" class="table table-striped mt-3">
  <thead>
    <tr>
      <th>Lot ID</th>
      <th>Spot ID</th>
      <th>Parking Start</th>
      <th>Parking Leaving</th>
      <th>Status</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="r in reservations" :key="r.id">
      <td>{{ r.lot_id || 'N/A' }}</td>
      <td>{{ r.spot_id }}</td>
      <td>{{ formatDate(r.parking_timestamp) }}</td>
      <td>{{ formatDate(r.leaving_timestamp) }}</td>
      <td>{{ r.status }}</td>
      <td>
        <button
          v-if="r.status === 'active'"
          class="btn btn-danger btn-sm"
          @click="releaseParking(r.id)"
        >
          Release
        </button>
        <button
          v-else
          class="btn btn-primary btn-sm"
          @click="bookSpot(r.lot_id)"
        >
          Rebook
        </button>
      </td>
    </tr>
  </tbody>
</table>

<div v-if="!loadingHistory && !reservations.length" class="alert alert-info">
  No bookings found.
</div>

</template>
