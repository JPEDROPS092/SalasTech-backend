<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Data
const myReservations = ref([]);
const loading = ref(false);
const totalRecords = ref(0);

// Tabs
const activeTab = ref(0);

// Filters
const filters = reactive({
  global: { value: null, matchMode: 'contains' },
  title: { value: null, matchMode: 'contains' },
  room: { value: null, matchMode: 'contains' },
  status: { value: null, matchMode: 'equals' }
});

// Pagination
const lazyParams = ref({
  first: 0,
  rows: 10,
  page: 1,
  sortField: 'start_time',
  sortOrder: -1
});

// Dialog visibility
const cancelReservationDialog = ref(false);
const reservationDetailsDialog = ref(false);

// Selected reservation for operations
const selectedReservation = ref(null);

// Fetch user's reservations
const loadMyReservations = async () => {
  if (!auth.isAuthenticated) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Você precisa estar autenticado para ver suas reservas',
      life: 3000
    });
    router.push('/login');
    return;
  }

  try {
    loading.value = true;
    
    // Implement API call to get user's reservations with pagination
    // const response = await api.getUserReservations(auth.user.id, lazyParams.value);
    // myReservations.value = response.data;
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
      
      myReservations.value = [
        {
          id: 1,
          title: 'Aula de Matemática',
          description: 'Aula de Cálculo I para turma de Engenharia',
          start_time: today.toISOString(),
          end_time: new Date(today.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: 'Sala 101',
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
          status: 'PENDING'
        },
        {
          id: 5,
          title: 'Monitoria de Matemática',
          description: 'Monitoria para alunos com dificuldade em Cálculo',
          start_time: yesterday.toISOString(),
          end_time: new Date(yesterday.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: 'Sala 101',
          status: 'CANCELLED'
        }
      ];
      
      totalRecords.value = 4;
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error loading reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar suas reservas',
      life: 3000
    });
    loading.value = false;
  }
};

// Handle page change
const onPage = (event) => {
  lazyParams.value.first = event.first;
  lazyParams.value.rows = event.rows;
  lazyParams.value.page = event.page + 1;
  loadMyReservations();
};

// Handle sort
const onSort = (event) => {
  lazyParams.value.sortField = event.sortField;
  lazyParams.value.sortOrder = event.sortOrder;
  loadMyReservations();
};

// Handle filter
const onFilter = () => {
  lazyParams.value.first = 0;
  lazyParams.value.page = 1;
  loadMyReservations();
};

// View reservation details
const viewReservation = (reservation) => {
  router.push(`/reservations/${reservation.id}`);
};

// View room details
const viewRoom = (id) => {
  router.push(`/rooms/${id}`);
};

// Open reservation details dialog
const openDetailsDialog = (reservation) => {
  selectedReservation.value = reservation;
  reservationDetailsDialog.value = true;
};

// Confirm cancel reservation
const confirmCancelReservation = (reservation) => {
  selectedReservation.value = reservation;
  cancelReservationDialog.value = true;
};

// Cancel reservation
const cancelReservation = async () => {
  try {
    // Implement API call to cancel reservation
    // await api.updateReservation(selectedReservation.value.id, { status: 'CANCELLED' });
    
    // Update local data
    const index = myReservations.value.findIndex(r => r.id === selectedReservation.value.id);
    if (index !== -1) {
      myReservations.value[index] = { 
        ...myReservations.value[index], 
        status: 'CANCELLED' 
      };
    }
    
    cancelReservationDialog.value = false;
    selectedReservation.value = null;
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva cancelada com sucesso',
      life: 3000
    });
  } catch (error) {
    console.error('Error cancelling reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível cancelar a reserva',
      life: 3000
    });
  }
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

// Filter reservations by status for tabs
const getFilteredReservations = (status = null) => {
  if (!status) return myReservations.value;
  return myReservations.value.filter(r => r.status === status);
};

// Check if reservation can be cancelled
const canCancelReservation = (reservation) => {
  return reservation.status !== 'CANCELLED';
};

// Create new reservation
const createNewReservation = () => {
  router.push('/rooms/search');
};

// Initialize component
onMounted(async () => {
  await loadMyReservations();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <Toast />
        <ConfirmDialog />
        
        <div class="flex justify-content-between align-items-center mb-4">
          <h5 class="m-0">Minhas Reservas</h5>
          <Button label="Nova Reserva" icon="pi pi-plus" class="p-button-success" @click="createNewReservation" v-if="auth.isAuthenticated" />
        </div>
        
        <TabView v-model:activeIndex="activeTab">
          <TabPanel header="Todas">
            <DataTable 
              :value="myReservations" 
              dataKey="id"
              :paginator="true" 
              :rows="10"
              :rowsPerPageOptions="[5, 10, 25]"
              paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
              currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} reservas"
              responsiveLayout="scroll"
              :loading="loading"
              :filters="filters"
              filterDisplay="menu"
              :globalFilterFields="['title', 'room']"
              @page="onPage"
              @sort="onSort"
              @filter="onFilter"
              :lazy="true"
              :totalRecords="totalRecords"
              :rowHover="true"
              stripedRows
              emptyMessage="Nenhuma reserva encontrada"
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
              
              <Column field="title" header="Título" :sortable="true" style="min-width: 12rem">
                <template #filter="{ filterModel, filterCallback }">
                  <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por título" class="p-column-filter" />
                </template>
              </Column>
              
              <Column field="room" header="Sala" :sortable="true" style="min-width: 10rem">
                <template #filter="{ filterModel, filterCallback }">
                  <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por sala" class="p-column-filter" />
                </template>
              </Column>
              
              <Column field="start_time" header="Início" :sortable="true" style="min-width: 10rem">
                <template #body="{ data }">
                  {{ formatDate(data.start_time) }}
                </template>
              </Column>
              
              <Column field="end_time" header="Término" :sortable="true" style="min-width: 10rem">
                <template #body="{ data }">
                  {{ formatDate(data.end_time) }}
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
                    :options="[
                      { label: 'Confirmada', value: 'CONFIRMED' },
                      { label: 'Pendente', value: 'PENDING' },
                      { label: 'Cancelada', value: 'CANCELLED' }
                    ]" 
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
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewReservation(data)" />
                    <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-success mr-2" @click="viewRoom(data.room_id)" />
                    <Button icon="pi pi-times" class="p-button-rounded p-button-text p-button-danger" @click="confirmCancelReservation(data)" v-if="canCancelReservation(data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Confirmadas">
            <DataTable 
              :value="getFilteredReservations('CONFIRMED')" 
              dataKey="id"
              :paginator="true" 
              :rows="10"
              responsiveLayout="scroll"
              :rowHover="true"
              stripedRows
              emptyMessage="Nenhuma reserva confirmada encontrada"
            >
              <Column field="title" header="Título" :sortable="true"></Column>
              <Column field="room" header="Sala" :sortable="true"></Column>
              <Column field="start_time" header="Início" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.start_time) }}
                </template>
              </Column>
              <Column field="end_time" header="Término" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.end_time) }}
                </template>
              </Column>
              <Column header="Ações" style="min-width: 10rem">
                <template #body="{ data }">
                  <div class="flex">
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewReservation(data)" />
                    <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-success mr-2" @click="viewRoom(data.room_id)" />
                    <Button icon="pi pi-times" class="p-button-rounded p-button-text p-button-danger" @click="confirmCancelReservation(data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Pendentes">
            <DataTable 
              :value="getFilteredReservations('PENDING')" 
              dataKey="id"
              :paginator="true" 
              :rows="10"
              responsiveLayout="scroll"
              :rowHover="true"
              stripedRows
              emptyMessage="Nenhuma reserva pendente encontrada"
            >
              <Column field="title" header="Título" :sortable="true"></Column>
              <Column field="room" header="Sala" :sortable="true"></Column>
              <Column field="start_time" header="Início" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.start_time) }}
                </template>
              </Column>
              <Column field="end_time" header="Término" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.end_time) }}
                </template>
              </Column>
              <Column header="Ações" style="min-width: 10rem">
                <template #body="{ data }">
                  <div class="flex">
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewReservation(data)" />
                    <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-success mr-2" @click="viewRoom(data.room_id)" />
                    <Button icon="pi pi-times" class="p-button-rounded p-button-text p-button-danger" @click="confirmCancelReservation(data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Canceladas">
            <DataTable 
              :value="getFilteredReservations('CANCELLED')" 
              dataKey="id"
              :paginator="true" 
              :rows="10"
              responsiveLayout="scroll"
              :rowHover="true"
              stripedRows
              emptyMessage="Nenhuma reserva cancelada encontrada"
            >
              <Column field="title" header="Título" :sortable="true"></Column>
              <Column field="room" header="Sala" :sortable="true"></Column>
              <Column field="start_time" header="Início" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.start_time) }}
                </template>
              </Column>
              <Column field="end_time" header="Término" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.end_time) }}
                </template>
              </Column>
              <Column header="Ações" style="min-width: 10rem">
                <template #body="{ data }">
                  <div class="flex">
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewReservation(data)" />
                    <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-success" @click="viewRoom(data.room_id)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
        </TabView>
        
        <!-- Cancel Reservation Dialog -->
        <Dialog v-model:visible="cancelReservationDialog" :style="{width: '450px'}" header="Cancelar Reserva" :modal="true">
          <div class="confirmation-content">
            <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
            <span v-if="selectedReservation">Tem certeza que deseja cancelar a reserva <b>{{ selectedReservation.title }}</b>?</span>
          </div>
          <template #footer>
            <Button label="Não" icon="pi pi-times" class="p-button-text" @click="cancelReservationDialog = false" />
            <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="cancelReservation" />
          </template>
        </Dialog>
        
        <!-- Reservation Details Dialog -->
        <Dialog v-model:visible="reservationDetailsDialog" :style="{width: '550px'}" header="Detalhes da Reserva" :modal="true">
          <div v-if="selectedReservation" class="reservation-details">
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Título:</label>
              <div class="col-12 md:col-8">{{ selectedReservation.title }}</div>
            </div>
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Descrição:</label>
              <div class="col-12 md:col-8">{{ selectedReservation.description }}</div>
            </div>
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Sala:</label>
              <div class="col-12 md:col-8">{{ selectedReservation.room }}</div>
            </div>
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Início:</label>
              <div class="col-12 md:col-8">{{ formatDate(selectedReservation.start_time) }}</div>
            </div>
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Término:</label>
              <div class="col-12 md:col-8">{{ formatDate(selectedReservation.end_time) }}</div>
            </div>
            <div class="field grid mb-2">
              <label class="col-12 md:col-4 font-bold">Status:</label>
              <div class="col-12 md:col-8">
                <Tag :value="getStatusLabel(selectedReservation.status)" :severity="getStatusSeverity(selectedReservation.status)" />
              </div>
            </div>
          </div>
          <template #footer>
            <Button label="Fechar" icon="pi pi-times" class="p-button-text" @click="reservationDetailsDialog = false" />
            <Button 
              label="Ver Detalhes Completos" 
              icon="pi pi-eye" 
              class="p-button-text" 
              @click="() => { reservationDetailsDialog = false; viewReservation(selectedReservation); }" 
            />
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

.p-tabview .p-tabview-nav {
  border-width: 0 0 2px 0;
}

.p-tabview .p-tabview-nav li .p-tabview-nav-link {
  border: none;
  background: transparent;
  transition: all 0.2s;
  border-radius: 0;
  padding: 1rem;
}

.p-tabview .p-tabview-nav li.p-highlight .p-tabview-nav-link {
  border-color: var(--primary-color);
  color: var(--primary-color);
  border-width: 0 0 2px 0;
  border-style: solid;
}

.p-column-filter {
  width: 100%;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.field.grid {
  margin: 0;
}
</style>
