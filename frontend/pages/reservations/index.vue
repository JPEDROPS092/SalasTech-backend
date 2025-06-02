<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Data
const reservations = ref([]);
const selectedReservations = ref([]);
const loading = ref(false);
const totalRecords = ref(0);

// Filters
const filters = reactive({
  global: { value: null, matchMode: 'contains' },
  title: { value: null, matchMode: 'contains' },
  room: { value: null, matchMode: 'contains' },
  status: { value: null, matchMode: 'equals' },
  date: { value: null, matchMode: 'dateIs' }
});

// Pagination
const lazyParams = ref({
  first: 0,
  rows: 10,
  page: 1,
  sortField: 'start_time',
  sortOrder: -1
});

// Status options
const statusOptions = ref([
  { label: 'Confirmada', value: 'CONFIRMED' },
  { label: 'Pendente', value: 'PENDING' },
  { label: 'Cancelada', value: 'CANCELLED' }
]);

// Dialog visibility
const deleteReservationDialog = ref(false);
const deleteReservationsDialog = ref(false);
const reservationDialog = ref(false);

// Selected reservation for operations
const reservation = ref({
  id: null,
  title: '',
  description: '',
  start_time: null,
  end_time: null,
  room_id: null,
  room: null,
  status: 'PENDING'
});

// Rooms for dropdown
const rooms = ref([]);

// Validation
const submitted = ref(false);

// Fetch reservations data
const loadReservations = async () => {
  try {
    loading.value = true;
    
    // Implement API call to get reservations with pagination
    // const response = await api.getReservations(lazyParams.value);
    // reservations.value = response.data;
    // totalRecords.value = response.total;
    
    // Mock data for now
    setTimeout(() => {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const nextWeek = new Date(today);
      nextWeek.setDate(nextWeek.getDate() + 7);
      
      reservations.value = [
        {
          id: 1,
          title: 'Aula de Matemática',
          description: 'Aula de Cálculo I para turma de Engenharia',
          start_time: today.toISOString(),
          end_time: new Date(today.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: 'Sala 101',
          user: 'Prof. Carlos Silva',
          status: 'CONFIRMED'
        },
        {
          id: 2,
          title: 'Aula de Programação',
          description: 'Aula de Programação Web para turma de Sistemas de Informação',
          start_time: yesterday.toISOString(),
          end_time: new Date(yesterday.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 2,
          room: 'Laboratório de Informática',
          user: 'Prof. João Pereira',
          status: 'CONFIRMED'
        },
        {
          id: 3,
          title: 'Palestra: Inteligência Artificial',
          description: 'Palestra sobre avanços em IA e suas aplicações',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 3 * 60 * 60 * 1000).toISOString(),
          room_id: 3,
          room: 'Auditório',
          user: 'Dr. Roberto Mendes',
          status: 'PENDING'
        },
        {
          id: 4,
          title: 'Reunião de Coordenação',
          description: 'Reunião mensal de coordenação de cursos',
          start_time: nextWeek.toISOString(),
          end_time: new Date(nextWeek.getTime() + 1.5 * 60 * 60 * 1000).toISOString(),
          room_id: 4,
          room: 'Sala de Reuniões',
          user: 'Coord. Maria Santos',
          status: 'PENDING'
        },
        {
          id: 5,
          title: 'Monitoria de Matemática',
          description: 'Monitoria para alunos com dificuldade em Cálculo',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: 'Sala 101',
          user: 'Monitor Pedro Santos',
          status: 'CANCELLED'
        }
      ];
      
      totalRecords.value = 5;
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error loading reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as reservas',
      life: 3000
    });
    loading.value = false;
  }
};

// Fetch rooms
const fetchRooms = async () => {
  try {
    // Implement API call to get rooms
    // const response = await api.getRooms();
    // rooms.value = response;
    
    // Mock data for now
    rooms.value = [
      { name: 'Sala 101', id: 1 },
      { name: 'Laboratório de Informática', id: 2 },
      { name: 'Auditório', id: 3 },
      { name: 'Sala de Reuniões', id: 4 },
      { name: 'Sala 102', id: 5 }
    ];
  } catch (error) {
    console.error('Error fetching rooms:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as salas',
      life: 3000
    });
  }
};

// Handle page change
const onPage = (event) => {
  lazyParams.value.first = event.first;
  lazyParams.value.rows = event.rows;
  lazyParams.value.page = event.page + 1;
  loadReservations();
};

// Handle sort
const onSort = (event) => {
  lazyParams.value.sortField = event.sortField;
  lazyParams.value.sortOrder = event.sortOrder;
  loadReservations();
};

// Handle filter
const onFilter = () => {
  lazyParams.value.first = 0;
  lazyParams.value.page = 1;
  loadReservations();
};

// Open new reservation dialog
const openNew = () => {
  reservation.value = {
    id: null,
    title: '',
    description: '',
    start_time: null,
    end_time: null,
    room_id: null,
    room: null,
    status: 'PENDING'
  };
  submitted.value = false;
  reservationDialog.value = true;
};

// Hide dialog
const hideDialog = () => {
  reservationDialog.value = false;
  submitted.value = false;
};

// Save reservation
const saveReservation = () => {
  submitted.value = true;

  if (reservation.value.title.trim() && reservation.value.start_time && reservation.value.end_time && reservation.value.room_id) {
    try {
      if (reservation.value.id) {
        // Update existing reservation
        // await api.updateReservation(reservation.value.id, reservation.value);
        
        // Update local data
        const index = reservations.value.findIndex(r => r.id === reservation.value.id);
        if (index !== -1) {
          // Find room name
          const room = rooms.value.find(r => r.id === reservation.value.room_id);
          reservation.value.room = room ? room.name : '';
          
          reservations.value[index] = { ...reservation.value };
        }
        
        toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Reserva atualizada',
          life: 3000
        });
      } else {
        // Create new reservation
        // const response = await api.createReservation(reservation.value);
        // reservation.value.id = response.id;
        
        // Mock new ID
        reservation.value.id = reservations.value.length + 1;
        
        // Find room name
        const room = rooms.value.find(r => r.id === reservation.value.room_id);
        reservation.value.room = room ? room.name : '';
        
        // Set user (in a real app, this would come from the backend)
        reservation.value.user = auth.user?.name || 'Usuário';
        
        // Add to local data
        reservations.value.push({ ...reservation.value });
        
        toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Reserva criada',
          life: 3000
        });
      }
      
      reservationDialog.value = false;
      reservation.value = {};
    } catch (error) {
      console.error('Error saving reservation:', error);
      toast.add({
        severity: 'error',
        summary: 'Erro',
        detail: 'Não foi possível salvar a reserva',
        life: 3000
      });
    }
  }
};

// Edit reservation
const editReservation = (editReservation) => {
  reservation.value = { ...editReservation };
  // Convert ISO strings to Date objects for the calendar component
  reservation.value.start_time = new Date(reservation.value.start_time);
  reservation.value.end_time = new Date(reservation.value.end_time);
  reservationDialog.value = true;
};

// Confirm delete reservation
const confirmDeleteReservation = (editReservation) => {
  reservation.value = editReservation;
  deleteReservationDialog.value = true;
};

// Delete reservation
const deleteReservation = async () => {
  try {
    // Implement API call to delete reservation
    // await api.deleteReservation(reservation.value.id);
    
    // Update local data
    reservations.value = reservations.value.filter(r => r.id !== reservation.value.id);
    
    deleteReservationDialog.value = false;
    reservation.value = {};
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva excluída',
      life: 3000
    });
  } catch (error) {
    console.error('Error deleting reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível excluir a reserva',
      life: 3000
    });
  }
};

// Confirm delete selected reservations
const confirmDeleteSelected = () => {
  deleteReservationsDialog.value = true;
};

// Delete selected reservations
const deleteSelectedReservations = async () => {
  try {
    // Implement API call to delete multiple reservations
    // await Promise.all(selectedReservations.value.map(reservation => api.deleteReservation(reservation.id)));
    
    // Update local data
    reservations.value = reservations.value.filter(r => !selectedReservations.value.includes(r));
    
    deleteReservationsDialog.value = false;
    selectedReservations.value = [];
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reservas excluídas',
      life: 3000
    });
  } catch (error) {
    console.error('Error deleting reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível excluir as reservas',
      life: 3000
    });
  }
};

// View reservation details
const viewReservation = (id) => {
  router.push(`/reservations/${id}`);
};

// View room details
const viewRoom = (id) => {
  router.push(`/rooms/${id}`);
};

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Get status severity
const getStatusSeverity = (status) => {
  switch (status) {
    case 'CONFIRMED':
      return 'success';
    case 'PENDING':
      return 'warning';
    case 'CANCELLED':
      return 'danger';
    default:
      return 'info';
  }
};

// Get status label
const getStatusLabel = (status) => {
  switch (status) {
    case 'CONFIRMED':
      return 'Confirmada';
    case 'PENDING':
      return 'Pendente';
    case 'CANCELLED':
      return 'Cancelada';
    default:
      return status;
  }
};

// Check if user can edit reservation
const canEditReservation = (reservationData) => {
  // In a real app, you would check if the user is the owner or has admin rights
  return auth.hasAdminAccess || (auth.user && reservationData.user === auth.user.name);
};

// Initialize component
onMounted(async () => {
  await fetchRooms();
  await loadReservations();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <Toast />
        <ConfirmDialog />
        
        <div class="flex justify-content-between align-items-center mb-4">
          <h5 class="m-0">Gerenciamento de Reservas</h5>
          <div>
            <Button label="Nova Reserva" icon="pi pi-plus" class="p-button-success mr-2" @click="openNew" v-if="auth.isAuthenticated" />
            <Button label="Excluir" icon="pi pi-trash" class="p-button-danger" @click="confirmDeleteSelected" 
                   :disabled="!selectedReservations || !selectedReservations.length" v-if="auth.hasAdminAccess" />
          </div>
        </div>
        
        <DataTable 
          :value="reservations" 
          v-model:selection="selectedReservations" 
          dataKey="id"
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} reservas"
          responsiveLayout="scroll"
          :loading="loading"
          :filters="filters"
          filterDisplay="menu"
          :globalFilterFields="['title', 'room', 'user']"
          @page="onPage"
          @sort="onSort"
          @filter="onFilter"
          :lazy="true"
          :totalRecords="totalRecords"
          :rowHover="true"
          stripedRows
        >
          <template #header>
            <div class="flex justify-content-between">
              <Button icon="pi pi-filter-slash" label="Limpar Filtros" class="p-button-outlined" @click="filters = {}" />
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Buscar..." />
              </span>
            </div>
          </template>
          
          <Column selectionMode="multiple" headerStyle="width: 3rem" v-if="auth.hasAdminAccess"></Column>
          
          <Column field="title" header="Título" :sortable="true" style="min-width: 12rem">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por título" class="p-column-filter" />
            </template>
          </Column>
          
          <Column field="room" header="Sala" :sortable="true" style="min-width: 10rem">
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown 
                v-model="filterModel.value" 
                @change="filterCallback()"
                :options="rooms" 
                optionLabel="name" 
                placeholder="Selecione uma sala" 
                class="p-column-filter" 
                showClear
              />
            </template>
          </Column>
          
          <Column field="start_time" header="Início" :sortable="true" style="min-width: 10rem">
            <template #body="{ data }">
              {{ formatDate(data.start_time) }}
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <Calendar 
                v-model="filterModel.value" 
                dateFormat="dd/mm/yy" 
                placeholder="Data de início" 
                @date-select="filterCallback()"
                class="p-column-filter" 
              />
            </template>
          </Column>
          
          <Column field="end_time" header="Término" :sortable="true" style="min-width: 10rem">
            <template #body="{ data }">
              {{ formatDate(data.end_time) }}
            </template>
          </Column>
          
          <Column field="user" header="Responsável" :sortable="true" style="min-width: 10rem">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por responsável" class="p-column-filter" />
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true" style="min-width: 8rem">
            <template #body="{ data }">
              <Tag :value="getStatusLabel(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown 
                v-model="filterModel.value" 
                @change="filterCallback()"
                :options="statusOptions" 
                optionLabel="label"
                optionValue="value"
                placeholder="Selecione um status" 
                class="p-column-filter" 
                showClear
              />
            </template>
          </Column>
          
          <Column header="Ações" style="min-width: 10rem">
            <template #body="{ data }">
              <div class="flex">
                <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewReservation(data.id)" />
                <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-success mr-2" @click="viewRoom(data.room_id)" />
                <Button icon="pi pi-pencil" class="p-button-rounded p-button-text p-button-warning mr-2" @click="editReservation(data)" v-if="canEditReservation(data)" />
                <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="confirmDeleteReservation(data)" v-if="canEditReservation(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
        
        <!-- Reservation Dialog -->
        <Dialog v-model:visible="reservationDialog" :style="{width: '550px'}" header="Detalhes da Reserva" :modal="true" class="p-fluid">
          <div class="field">
            <label for="title">Título</label>
            <InputText id="title" v-model="reservation.title" required autofocus :class="{'p-invalid': submitted && !reservation.title}" />
            <small class="p-error" v-if="submitted && !reservation.title">Título é obrigatório.</small>
          </div>
          
          <div class="field">
            <label for="description">Descrição</label>
            <Textarea id="description" v-model="reservation.description" rows="3" />
          </div>
          
          <div class="field">
            <label for="room">Sala</label>
            <Dropdown id="room" v-model="reservation.room_id" :options="rooms" optionLabel="name" optionValue="id" placeholder="Selecione uma sala" :class="{'p-invalid': submitted && !reservation.room_id}" />
            <small class="p-error" v-if="submitted && !reservation.room_id">Sala é obrigatória.</small>
          </div>
          
          <div class="field">
            <label for="start_time">Data e Hora de Início</label>
            <Calendar id="start_time" v-model="reservation.start_time" showTime hourFormat="24" :class="{'p-invalid': submitted && !reservation.start_time}" />
            <small class="p-error" v-if="submitted && !reservation.start_time">Data e hora de início são obrigatórias.</small>
          </div>
          
          <div class="field">
            <label for="end_time">Data e Hora de Término</label>
            <Calendar id="end_time" v-model="reservation.end_time" showTime hourFormat="24" :class="{'p-invalid': submitted && !reservation.end_time}" />
            <small class="p-error" v-if="submitted && !reservation.end_time">Data e hora de término são obrigatórias.</small>
          </div>
          
          <div class="field" v-if="auth.hasAdminAccess">
            <label for="status">Status</label>
            <Dropdown id="status" v-model="reservation.status" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Selecione um status" />
          </div>
          
          <template #footer>
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
            <Button label="Salvar" icon="pi pi-check" class="p-button-text" @click="saveReservation" />
          </template>
        </Dialog>
        
        <!-- Delete Reservation Dialog -->
        <Dialog v-model:visible="deleteReservationDialog" :style="{width: '450px'}" header="Confirmar" :modal="true">
          <div class="confirmation-content">
            <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
            <span v-if="reservation">Tem certeza que deseja excluir a reserva <b>{{ reservation.title }}</b>?</span>
          </div>
          <template #footer>
            <Button label="Não" icon="pi pi-times" class="p-button-text" @click="deleteReservationDialog = false" />
            <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="deleteReservation" />
          </template>
        </Dialog>
        
        <!-- Delete Multiple Reservations Dialog -->
        <Dialog v-model:visible="deleteReservationsDialog" :style="{width: '450px'}" header="Confirmar" :modal="true">
          <div class="confirmation-content">
            <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
            <span v-if="selectedReservations && selectedReservations.length">Tem certeza que deseja excluir as reservas selecionadas?</span>
          </div>
          <template #footer>
            <Button label="Não" icon="pi pi-times" class="p-button-text" @click="deleteReservationsDialog = false" />
            <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="deleteSelectedReservations" />
          </template>
        </Dialog>
      </div>
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

.p-datatable .p-datatable-thead > tr > th {
  background: var(--surface-ground);
  color: var(--text-color);
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.p-datatable .p-datatable-tbody > tr > td {
  padding: 0.75rem 1rem;
}

.p-dialog .p-dialog-header {
  border-bottom: 1px solid var(--surface-border);
  padding: 1.5rem;
}

.p-dialog .p-dialog-footer {
  border-top: 1px solid var(--surface-border);
  padding: 1.5rem;
  text-align: right;
}

.p-column-filter {
  width: 100%;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
