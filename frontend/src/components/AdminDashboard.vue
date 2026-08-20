<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { authorizedFetch } from '../utils/api';
import AdminNavbar from './AdminNavbar.vue';

const router = useRouter()
const lots = ref([])
const editingLotId = ref(null)
const editedData = ref({})
const addingLot = ref(false)

const newLot = ref({
  name: '',
  location: '',
  address: '',
  pin_code: '',
  price: '',
  total_spots: ''
})

async function loadLots() {
  try {
    const res = await authorizedFetch('http://127.0.0.1:5000/api/admin/lots')
    if (res.ok) {
      lots.value = await res.json()
    } else {
      console.error('Failed to load lots:', res.status)
    }
  } catch (err) {
    console.error('Error loading lots:', err)
  }
}

onMounted(loadLots)

function editLot(lot) {
  editingLotId.value = lot.id
  editedData.value = { ...lot }
}

function cancelEdit() {
  editingLotId.value = null
  editedData.value = {}
}

async function saveLot(lotId) {
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/admin/lots/${lotId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editedData.value)
    })
    if (res.ok) {
      await loadLots()
      cancelEdit()
    } else {
      alert('Update failed')
    }
  } catch (err) {
    console.error('Error updating lot:', err)
  }
}

async function deleteLot(id) {
  if (!confirm('Are you sure you want to delete this lot?')) return
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/admin/lots/${id}`, { method: 'DELETE' })
    if (res.ok) {
      lots.value = lots.value.filter(l => l.id !== id)
      cancelEdit()
    } else {
      const err = await res.json()
      alert(err.error || 'Delete failed.')
    }
  } catch (err) {
    console.error('Error deleting lot:', err)
    alert('Something went wrong. Please try again.')
  }
}

function startAddLot() {
  addingLot.value = true
  newLot.value = {
    name: '',
    location: '',
    address: '',
    pin_code: '',
    price: '',
    total_spots: ''
  }
}

</script>

<template>
  <div>
    <AdminNavbar />
    <div class="container mt-4">
      <h2 class="text-center mb-4">Parking Lots</h2>
      <div class="row">
        <div class="col-md-6 col-lg-4 mb-4" v-for="lot in lots" :key="lot.id">
          <div class="card h-100 shadow">
            <div class="card-body d-flex flex-column">
              <h3 class="card-title text-center">{{ lot.name }}</h3>
              <div class="row mb-1">
                <div class="col-5 text-end fw-bold">Location:</div>
                <div class="col-7">{{ lot.location }}</div>
              </div>
              <div class="row mb-1">
                <div class="col-5 text-end fw-bold">Address:</div>
                <div class="col-7">{{ lot.address }}</div>
              </div>
              <div class="row mb-1">
                <div class="col-5 text-end fw-bold">Pincode:</div>
                <div class="col-7">{{ lot.pin_code }}</div>
              </div>
              <div class="row mb-1">
                <div class="col-5 text-end fw-bold">Price/hrs:</div>
                <div class="col-7">₹{{ lot.price }}</div>
              </div>
              <div class="row mb-3">
                <div class="col-5 text-end fw-bold">Occupied:</div>
                <div class="col-7">{{ lot.occupied_spots }} / {{ lot.total_spots }}</div>
              </div>
              <div class="d-flex justify-content-center mb-3">
                <div class="d-grid overflow-auto" style="grid-template-columns: repeat(4, 40px); gap: 0.5rem; max-height: 200px;">
                  <div v-for="n in lot.total_spots" :key="n" class="rounded text-center" :class="{ 'bg-success text-white': n <= lot.occupied_spots, 'bg-light border': n > lot.occupied_spots}" style="width: 40px; height: 40px; line-height: 40px;">
                    {{ n }}
                  </div>
                </div>
              </div>
              <div v-if="editingLotId === lot.id">
                <input v-model="editedData.name" placeholder="Name" class="form-control mb-2" />
                <input v-model="editedData.location" placeholder="Location" class="form-control mb-2" />
                <input v-model="editedData.address" placeholder="Address" class="form-control mb-2" />
                <input v-model.number="editedData.pin_code" placeholder="Pincode" class="form-control mb-2" />
                <input v-model.number="editedData.price" placeholder="Price" class="form-control mb-2" />
                <input v-model.number="editedData.total_spots" placeholder="Total Spots" class="form-control mb-3" />
                <div class="d-flex justify-content-between">
                  <button class="btn btn-success btn-sm" @click="saveLot(lot.id)">Save</button>
                  <button class="btn btn-secondary btn-sm" @click="cancelEdit">Cancel</button>
                  <button class="btn btn-danger btn-sm" @click="deleteLot(lot.id)">Delete</button>
                </div>
              </div>
              <div v-else class="text-center mt-auto">
                <button class="btn btn-sm btn-warning" @click="editLot(lot)">Edit</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex justify-content-center align-items-center mt-4">
        <RouterLink to="/add_lot" class="btn btn-primary text-center">Add New Lot</RouterLink>
      </div>
    </div>
  </div>
</template>
