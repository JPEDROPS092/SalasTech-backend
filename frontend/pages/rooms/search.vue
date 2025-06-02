<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Search form
const searchForm = reactive({
  date: new Date(),
  startTime: null,
  endTime: null,
  capacity: 0,
  department: null,
  resources: []
});

// Search results
const searchResults = ref([]);
const loading = ref(false);
const searched = ref(false);

// Departments for filter
const departments = ref([]);

// Resources options
const resourceOptions = ref([
  { name: 'Projetor', id: 1 },
  { name: 'Computador', id: 2 },
  { name: 'Ar Condicionado', id: 3 },
  { name: 'Smart TV', id: 4 },
  { name: 'Sistema de Som', id: 5 },
  { name: 'Quadro Branco', id: 6 },
  { name: 'Mesa de Reunião', id: 7 }
]);

// Time slots for dropdown
const timeSlots = ref([]);

// Validation
const submitted = ref(false);

// Selected room for reservation
const selectedRoom = ref(null);
const reservationDialog = ref(false);
const newReservation = reactive({
  title: '',
  description: '',
  date: null,
  startTime: null,
  endTime: null,
  room_id: null
});

// Initialize time slots
const initTimeSlots = () => {
  const slots = [];
  for (let hour = 7; hour < 22; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const hourStr = hour.toString().padStart(2, '0');
      const minuteStr = minute.toString().padStart(2, '0');
      const timeStr = `${hourStr}:${minuteStr}`;
      slots.push({ label: timeStr, value: timeStr });
    }
  }
  timeSlots.value = slots;
};

// Fetch departments
const fetchDepartments = async () => {
  try {
    // Implement API call to get departments
    // const response = await api.getDepartments();
    // departments.value = response;
    
    // Mock data for now
    departments.value = [
      { name: 'Departamento de TI', id: 1 },
      { name: 'Departamento Acadêmico', id: 2 },
      { name: 'Departamento Administrativo', id: 3 }
    ];
  } catch (error) {
    console.error('Error fetching departments:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar os departamentos',
      life: 3000
    });
  }
};

// Search for available rooms
const searchRooms = async () => {
  submitted.value = true;
  
  // Validate form
  if (!searchForm.date || !searchForm.startTime || !searchForm.endTime) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Por favor, preencha a data e os horários de início e término',
      life: 3000
    });
    return;
  }
  
  // Validate time range
  if (searchForm.startTime >= searchForm.endTime) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'O horário de início deve ser anterior ao horário de término',
      life: 3000
    });
    return;
  }
  
  try {
    loading.value = true;
    
    // Implement API call to search for available rooms
    // const response = await api.searchAvailableRooms({
    //   date: searchForm.date,
    //   start_time: searchForm.startTime,
    //   end_time: searchForm.endTime,
    //   capacity: searchForm.capacity > 0 ? searchForm.capacity : undefined,
    //   department_id: searchForm.department,
    //   resources: searchForm.resources.length > 0 ? searchForm.resources : undefined
    // });
    // searchResults.value = response;
    
    // Mock data for now
    setTimeout(() => {
      // Generate mock results based on search criteria
      const mockRooms = [
        { 
          id: 1, 
          name: 'Sala 101', 
          description: 'Sala de aula padrão', 
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'AVAILABLE',
          location: 'Bloco A, 1º Andar'
        },
        { 
          id: 2, 
          name: 'Laboratório de Informática', 
          description: 'Laboratório com 30 computadores', 
          capacity: 30, 
          department: 'Departamento de TI',
          department_id: 1,
          resources: [1, 2, 3, 4],
          status: 'AVAILABLE',
          location: 'Bloco B, Térreo'
        },
        { 
          id: 3, 
          name: 'Auditório', 
          description: 'Auditório principal', 
          capacity: 120, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 3, 4, 5],
          status: 'AVAILABLE',
          location: 'Bloco Central, Térreo'
        },
        { 
          id: 4, 
          name: 'Sala de Reuniões', 
          description: 'Sala para reuniões e videoconferências', 
          capacity: 15, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 2, 3, 4, 7],
          status: 'AVAILABLE',
          location: 'Bloco Administrativo, 2º Andar'
        },
        { 
          id: 5, 
          name: 'Sala 102', 
          description: 'Sala de aula padrão', 
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'AVAILABLE',
          location: 'Bloco A, 1º Andar'
        }
      ];
      
      // Filter based on capacity
      let filteredRooms = mockRooms;
      if (searchForm.capacity > 0) {
        filteredRooms = filteredRooms.filter(room => room.capacity >= searchForm.capacity);
      }
      
      // Filter based on department
      if (searchForm.department) {
        filteredRooms = filteredRooms.filter(room => room.department_id === searchForm.department);
      }
      
      // Filter based on resources
      if (searchForm.resources.length > 0) {
        filteredRooms = filteredRooms.filter(room => 
          searchForm.resources.every(resourceId => room.resources.includes(resourceId))
        );
      }
      
      // Randomly remove some rooms to simulate availability
      const randomUnavailable = Math.floor(Math.random() * filteredRooms.length);
      filteredRooms = filteredRooms.filter((_, index) => index !== randomUnavailable);
      
      searchResults.value = filteredRooms;
      searched.value = true;
      loading.value = false;
    }, 1000);
  } catch (error) {
    console.error('Error searching rooms:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível buscar salas disponíveis',
      life: 3000
    });
    loading.value = false;
  }
};

// Reset search form
const resetSearch = () => {
  searchForm.date = new Date();
  searchForm.startTime = null;
  searchForm.endTime = null;
  searchForm.capacity = 0;
  searchForm.department = null;
  searchForm.resources = [];
  submitted.value = false;
};

// View room details
const viewRoom = (id) => {
  router.push(`/rooms/${id}`);
};

// View room calendar
const viewRoomCalendar = (id) => {
  router.push(`/rooms/${id}/calendar`);
};

// Open reservation dialog
const openReservationDialog = (room) => {
  if (!auth.isAuthenticated) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Você precisa estar logado para criar reservas',
      life: 3000
    });
    return;
  }
  
  selectedRoom.value = room;
  
  // Initialize reservation form with search criteria
  newReservation.date = searchForm.date;
  newReservation.startTime = searchForm.startTime;
  newReservation.endTime = searchForm.endTime;
  newReservation.room_id = room.id;
  newReservation.title = '';
  newReservation.description = '';
  
  reservationDialog.value = true;
};

// Create reservation
const createReservation = async () => {
  submitted.value = true;
  
  if (!newReservation.title.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Por favor, informe um título para a reserva',
      life: 3000
    });
    return;
  }
  
  try {
    // Implement API call to create reservation
    // const combinedStartTime = combineDateTime(newReservation.date, newReservation.startTime);
    // const combinedEndTime = combineDateTime(newReservation.date, newReservation.endTime);
    // 
    // await api.createReservation({
    //   title: newReservation.title,
    //   description: newReservation.description,
    //   start_time: combinedStartTime,
    //   end_time: combinedEndTime,
    //   room_id: newReservation.room_id
    // });
    
    // Mock success
    setTimeout(() => {
      toast.add({
        severity: 'success',
        summary: 'Sucesso',
        detail: 'Reserva criada com sucesso',
        life: 3000
      });
      
      reservationDialog.value = false;
      submitted.value = false;
      
      // Remove the reserved room from results
      searchResults.value = searchResults.value.filter(room => room.id !== selectedRoom.value.id);
    }, 500);
  } catch (error) {
    console.error('Error creating reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível criar a reserva',
      life: 3000
    });
  }
};

// Format date
const formatDate = (date) => {
  if (!date) return '';
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date);
};

// Get resource names
const getResourceNames = (resourceIds) => {
  if (!resourceIds || !resourceIds.length) return '';
  
  return resourceIds
    .map(id => {
      const resource = resourceOptions.value.find(r => r.id === id);
      return resource ? resource.name : '';
    })
    .filter(Boolean)
    .join(', ');
};

// Initialize component
onMounted(() => {
  initTimeSlots();
  fetchDepartments();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <Toast />
      
      <div class="card">
        <h2 class="mb-4">Buscar Salas Disponíveis</h2>
        
        <div class="grid">
          <!-- Search Form -->
          <div class="col-12 lg:col-4">
            <div class="card p-fluid">
              <h3>Critérios de Busca</h3>
              
              <div class="field">
                <label for="date">Data</label>
                <Calendar id="date" v-model="searchForm.date" :showIcon="true" :class="{'p-invalid': submitted && !searchForm.date}" />
                <small class="p-error" v-if="submitted && !searchForm.date">Data é obrigatória.</small>
              </div>
              
              <div class="field">
                <label for="startTime">Horário de Início</label>
                <Dropdown id="startTime" v-model="searchForm.startTime" :options="timeSlots" optionLabel="label" optionValue="value" placeholder="Selecione o horário" :class="{'p-invalid': submitted && !searchForm.startTime}" />
                <small class="p-error" v-if="submitted && !searchForm.startTime">Horário de início é obrigatório.</small>
              </div>
              
              <div class="field">
                <label for="endTime">Horário de Término</label>
                <Dropdown id="endTime" v-model="searchForm.endTime" :options="timeSlots" optionLabel="label" optionValue="value" placeholder="Selecione o horário" :class="{'p-invalid': submitted && !searchForm.endTime}" />
                <small class="p-error" v-if="submitted && !searchForm.endTime">Horário de término é obrigatório.</small>
              </div>
              
              <div class="field">
                <label for="capacity">Capacidade Mínima</label>
                <InputNumber id="capacity" v-model="searchForm.capacity" :min="0" placeholder="Número de pessoas" />
              </div>
              
              <div class="field">
                <label for="department">Departamento</label>
                <Dropdown id="department" v-model="searchForm.department" :options="departments" optionLabel="name" optionValue="id" placeholder="Selecione um departamento" showClear />
              </div>
              
              <div class="field">
                <label for="resources">Recursos Necessários</label>
                <MultiSelect id="resources" v-model="searchForm.resources" :options="resourceOptions" optionLabel="name" optionValue="id" placeholder="Selecione os recursos" display="chip" />
              </div>
              
              <div class="flex justify-content-between">
                <Button label="Limpar" icon="pi pi-refresh" class="p-button-outlined" @click="resetSearch" />
                <Button label="Buscar" icon="pi pi-search" class="p-button-primary" @click="searchRooms" :loading="loading" />
              </div>
            </div>
          </div>
          
          <!-- Search Results -->
          <div class="col-12 lg:col-8">
            <div class="card">
              <h3>Salas Disponíveis</h3>
              
              <div v-if="loading" class="flex justify-content-center">
                <ProgressSpinner style="width: 50px; height: 50px" />
              </div>
              
              <div v-else-if="searched && searchResults.length === 0" class="p-4 surface-200 border-round text-center">
                <i class="pi pi-search text-xl mb-3 block"></i>
                <p class="m-0">Nenhuma sala disponível encontrada com os critérios informados.</p>
                <p class="mt-2">Tente modificar os critérios de busca.</p>
              </div>
              
              <div v-else-if="!searched" class="p-4 surface-200 border-round text-center">
                <i class="pi pi-info-circle text-xl mb-3 block"></i>
                <p class="m-0">Utilize os filtros ao lado para buscar salas disponíveis.</p>
              </div>
              
              <div v-else class="grid">
                <div v-for="room in searchResults" :key="room.id" class="col-12 md:col-6 xl:col-4 mb-3">
                  <div class="p-3 border-round surface-card h-full flex flex-column room-card">
                    <div class="flex justify-content-between align-items-center mb-3">
                      <h4 class="m-0">{{ room.name }}</h4>
                      <Tag value="Disponível" severity="success" />
                    </div>
                    
                    <p class="text-color-secondary mb-3">{{ room.description }}</p>
                    
                    <div class="mb-2">
                      <i class="pi pi-users mr-2"></i>
                      <span>Capacidade: {{ room.capacity }} pessoas</span>
                    </div>
                    
                    <div class="mb-2">
                      <i class="pi pi-building mr-2"></i>
                      <span>{{ room.department }}</span>
                    </div>
                    
                    <div class="mb-2">
                      <i class="pi pi-map-marker mr-2"></i>
                      <span>{{ room.location }}</span>
                    </div>
                    
                    <div class="mb-3">
                      <i class="pi pi-list mr-2"></i>
                      <span>{{ getResourceNames(room.resources) }}</span>
                    </div>
                    
                    <div class="flex justify-content-between mt-auto pt-3 border-top-1 surface-border">
                      <Button icon="pi pi-eye" class="p-button-text p-button-rounded" @click="viewRoom(room.id)" />
                      <Button icon="pi pi-calendar" class="p-button-text p-button-rounded" @click="viewRoomCalendar(room.id)" />
                      <Button icon="pi pi-check" label="Reservar" class="p-button-success" @click="openReservationDialog(room)" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Reservation Dialog -->
      <Dialog v-model:visible="reservationDialog" :style="{width: '450px'}" header="Nova Reserva" :modal="true" class="p-fluid">
        <div v-if="selectedRoom" class="mb-4">
          <h5 class="mb-2">{{ selectedRoom.name }}</h5>
          <p class="text-color-secondary mb-2">{{ selectedRoom.description }}</p>
          <div class="flex align-items-center mb-2">
            <i class="pi pi-calendar mr-2"></i>
            <span>{{ formatDate(newReservation.date) }}</span>
          </div>
          <div class="flex align-items-center">
            <i class="pi pi-clock mr-2"></i>
            <span>{{ newReservation.startTime }} - {{ newReservation.endTime }}</span>
          </div>
        </div>
        
        <div class="field">
          <label for="title">Título da Reserva*</label>
          <InputText id="title" v-model="newReservation.title" required autofocus :class="{'p-invalid': submitted && !newReservation.title}" />
          <small class="p-error" v-if="submitted && !newReservation.title">Título é obrigatório.</small>
        </div>
        
        <div class="field">
          <label for="description">Descrição</label>
          <Textarea id="description" v-model="newReservation.description" rows="3" />
        </div>
        
        <template #footer>
          <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="reservationDialog = false" />
          <Button label="Confirmar Reserva" icon="pi pi-check" @click="createReservation" />
        </template>
      </Dialog>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--surface-card);
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-radius: 10px;
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.02), 0px 0px 2px rgba(0, 0, 0, 0.05), 0px 1px 4px rgba(0, 0, 0, 0.08);
}

.room-card {
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.room-card:hover {
  transform: translateY(-3px);
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--text-color);
  font-weight: 600;
}

h4 {
  color: var(--text-color);
  font-weight: 600;
}

.border-top-1 {
  border-top: 1px solid var(--surface-border);
}
</style>
