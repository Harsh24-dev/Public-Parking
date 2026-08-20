<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authorizedFetch } from '../utils/api';
import UserNavbar from './UserNavbar.vue';

const reservations = ref([]);
const lots = ref([]);
const search = ref('');
const lotsError = ref('');
const historyError = ref('');
const loadingHistory = ref(true);

const router = useRouter();

async function fetchLots() {
  lotsError.value = '';
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/user/lots');
    if (res.ok) {
      lots.value = await res.json();
    } else {
      lotsError.value = `Failed to load lots (${res.status})`;
    }
  } catch (err) {
    lotsError.value = 'Error loading lots.';
    console.error(err);
  }
}

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

async function bookSpot(lotId) {
  if (!confirm('Are you sure you want to book a spot in this lot?')) return;
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/user/book/${lotId}`, {
      method: 'POST'
    });
    if (res.ok) {
      const data = await res.json();
      alert(`Booking successful! Reservation ID: ${data.Reservation_id}`);
      await fetchReservations();
      await fetchLots();
    } else {
      const err = await res.json();
      alert(err.error || 'Failed to book a spot.');
    }
  } catch (err) {
    console.error(err);
    alert('Something went wrong.');
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
      await fetchLots();
    } else {
      const err = await res.json();
      alert(err.error || 'Release failed.');
    }
  } catch (err) {
    console.error(err);
    alert('Something went wrong during release.');
  }
}

function formatDate(dateStr) {
  return dateStr ? new Date(dateStr).toLocaleString() : '';
}

const filteredLots = computed(() => {
  if (!search.value.trim()) return lots.value;
  return lots.value.filter(lot =>
    lot.name.toLowerCase().includes(search.value.toLowerCase())
  );
});

const activeReservations = computed(() =>
  reservations.value.filter(r => r.status === 'active')
);

onMounted(() => {
  fetchLots();
  fetchReservations();
});
</script>

<template>
  <div>
    <UserNavbar />

    <!-- Active Bookings -->
    <div class="container mt-4">
      <h3 class="text-center mb-4">Currently Booked/Active Slots</h3>
      <div v-if="historyError" class="alert alert-danger">{{ historyError }}</div>

      <table v-if="!loadingHistory && activeReservations.length" class="table table-striped mt-3">
        <thead>
          <tr>
            <th>Lot ID</th>
            <th>Spot ID</th>
            <th>Parking Start</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in activeReservations" :key="r.id">
            <td>{{ r.lot_id || 'N/A' }}</td>
            <td>{{ r.spot_id }}</td>
            <td>{{ formatDate(r.parking_timestamp) }}</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="releaseParking(r.id)">
                Release
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loadingHistory && !activeReservations.length" class="alert alert-info">
        No active bookings found.
      </div>
    </div>

    <!-- Available Lots -->
    <div class="container mt-4">
      <h3 class="text-center mb-4">Available Parking Lots</h3>
      <div v-if="lotsError" class="alert alert-danger">{{ lotsError }}</div>

      <div class="mb-4">
        <input type="text" class="form-control" placeholder="Search by parking location or name..." v-model="search"/>
      </div>

      <div class="row">
        <div v-if="filteredLots.length === 0" class="col-12 text-center">
          <p class="text-muted">No parking lots found.</p>
        </div>
        <div class="col-md-4 mb-4" v-for="lot in filteredLots" :key="lot.id">
          <div class="card h-100 shadow">
            <div class="card-body d-flex flex-column justify-content-between">
              <h5 class="text-center">{{ lot.name }}</h5>
              <div class="text-center">
                <p>Location: {{ lot.location }}</p>
                <p>Address: {{ lot.address }}</p>
                <p>Pincode: {{ lot.pin_code }}</p>
                <p>Available Spots: <strong>{{ lot.spots_status }}</strong></p>
                <p>Price: <strong>₹{{ lot.price }}/hr</strong></p>
              </div>
              <button
                class="btn btn-primary w-100 mt-auto"
                @click="bookSpot(lot.id)"
                :disabled="lot.spots_status <= 0"
              >
                Book Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</div>
</template>
