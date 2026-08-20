<script setup>
import { ref } from 'vue'
import { authorizedFetch } from '../utils/api'
import AdminNavbar from './AdminNavbar.vue'

const query = ref('')
const results = ref([])
const searched = ref(false)
const editingLotId = ref(null)
const editedData = ref({})

async function search() {
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/admin/search?q=${query.value}`)
    if (!res.ok) throw new Error('Search failed')
    results.value = await res.json()
    searched.value = true
  } catch (error) {
    console.error('Search error:', error)
    results.value = []
    searched.value = true
  }
}

function startEdit(lot) {
  editingLotId.value = lot.lot_id
  editedData.value = { ...lot }
}

function cancelEdit() {
  editingLotId.value = null
  editedData.value = {}
}

async function saveEdit(lotId) {
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/admin/lots/${lotId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editedData.value)
    })
    if (res.ok) {
      await search()
      cancelEdit()
    } else {
      alert('Failed to update lot')
    }
  } catch (err) {
    console.error('Error updating lot:', err)
  }
}

async function deleteLot(lotId) {
  if (!confirm('Are you sure you want to delete this lot?')) return
  try {
    const res = await authorizedFetch(`http://127.0.0.1:5000/api/admin/lots/${lotId}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      results.value = results.value.filter(lot => lot.lot_id !== lotId)
      cancelEdit()
    } else {
      alert('Delete failed')
    }
  } catch (err) {
    console.error('Error deleting lot:', err)
  }
}
</script>

<template>
  <div>
    <AdminNavbar />
    <div class="container mt-4">
      <h2 class="text-center mb-4">Search Parking Lots</h2>

      <div class="input-group mb-4">
        <input
          v-model="query"
          type="text"
          class="form-control"
          placeholder="Enter Lot ID, Name, or Location"
        />
        <button class="btn btn-outline-primary" @click="search">Search</button>
      </div>

      <div v-if="results.length" class="row">
        <div class="col-md-6 col-lg-4 mb-4" v-for="lot in results" :key="lot.lot_id">
          <div class="card h-100 shadow">
            <div class="card-body d-flex flex-column">
              <h3 class="card-title text-center">Lot #{{ lot.lot_id }}</h3>

              <div v-if="editingLotId === lot.lot_id">
                <input v-model="editedData.lot_name" class="form-control mb-2" placeholder="Name" />
                <input v-model="editedData.lot_location" class="form-control mb-2" placeholder="Location" />
                <input v-model.number="editedData.pin_code" class="form-control mb-2" placeholder="Pin Code" />
                <input v-model.number="editedData.price" class="form-control mb-2" placeholder="Price" />
                <input v-model.number="editedData.total_spots" class="form-control mb-2" placeholder="Total Spots" />
                <div class="d-flex justify-content-between mt-2">
                  <button class="btn btn-sm btn-success" @click="saveEdit(lot.lot_id)">Save</button>
                  <button class="btn btn-sm btn-secondary" @click="cancelEdit">Cancel</button>
                  <button class="btn btn-sm btn-danger" @click="deleteLot(lot.lot_id)">Delete</button>
                </div>
              </div>

              <div v-else>
                <div class="row mb-1">
                  <div class="col-5 text-end fw-bold">Name:</div>
                  <div class="col-7">{{ lot.lot_name }}</div>
                </div>
                <div class="row mb-1">
                  <div class="col-5 text-end fw-bold">Location:</div>
                  <div class="col-7">{{ lot.lot_location }}</div>
                </div>
                <div class="row mb-1">
                  <div class="col-5 text-end fw-bold">Occupied:</div>
                  <div class="col-7">{{ lot.occupied_spots }} / {{ lot.total_spots }}</div>
                </div>

                <div class="d-grid overflow-auto my-3"
                  style="grid-template-columns: repeat(4, 40px); gap: 0.5rem; max-height: 200px;">
                  <div v-for="n in lot.total_spots" :key="n" class="rounded text-center"
                    :class="{ 'bg-success text-white': n <= lot.occupied_spots, 'bg-light border': n > lot.occupied_spots }"
                    style="width: 40px; height: 40px; line-height: 40px;">
                    {{ n }}
                  </div>
                </div>

                <div class="text-center mt-auto">
                  <button class="btn btn-warning btn-sm" @click="startEdit(lot)">Edit</button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      <div v-else-if="searched" class="text-center text-muted">
        <p>No results found for "{{ query }}".</p>
      </div>
    </div>
  </div>
</template>
