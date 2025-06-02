<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'nuxt/app';
import { useReservationStore } from '~/stores/reservation';
import { useToast } from 'primevue/usetoast';
import { useAuth } from '~/composables/use-auth';

// Definir metadados da página
definePageMeta({
  middleware: ['auth'],
  public: false
});

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
  try {
    if (!auth.user?.id) {
      toast.add({ severity: 'error', summary: 'Erro', detail: 'Usuário não identificado', life: 3000 });
      return;
    }
    
    // Converter parâmetros de lazy loading para formato da API
    const page = Math.floor(lazyParams.value.first / lazyParams.value.rows) + 1;
    const limit = lazyParams.value.rows;
    const sortField = lazyParams.value.sortField;
    const sortOrder = lazyParams.value.sortOrder;
    
    // Carregar reservas do usuário da API
    await reservationStore.fetchUserReservations(auth.user.id, page, limit, sortField, sortOrder);
  } catch (error) {
    console.error('Erro ao carregar minhas reservas:', error);
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível carregar suas reservas', life: 3000 });
  }
};

// Manipulação de eventos da tabela
const onPage = (event) => {
  lazyParams.value.first = event.first;
  lazyParams.value.rows = event.rows;
  loadMyReservations();
};

const onSort = (event) => {
  lazyParams.value.sortField = event.sortField;
  lazyParams.value.sortOrder = event.sortOrder;
  loadMyReservations();
};

// Abrir diálogo de cancelamento
const openCancelDialog = (reservation) => {
  selectedReservation.value = reservation;
  cancelDialog.value = true;
};

// Cancelar reserva
const cancelReservation = async () => {
  try {
    if (!selectedReservation.value?.id) return;
    
    // Cancelar a reserva na API
    await reservationStore.cancelReservation(selectedReservation.value.id);
    
    cancelDialog.value = false;
    selectedReservation.value = null;
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Reserva cancelada', life: 3000 });
    
    // Recarregar para atualizar a lista
    loadMyReservations();
  } catch (error) {
    console.error('Erro ao cancelar reserva:', error);
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível cancelar a reserva', life: 3000 });
  }
};

// Fechar diálogo
const hideDialog = () => {
  cancelDialog.value = false;
  selectedReservation.value = null;
};

// Formatação
const formatDate = (value) => {
  return new Date(value).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getSeverity = (status) => {
  switch (status) {
    case 'CONFIRMED':
      return 'success';
    case 'PENDING':
      return 'warning';
    case 'CANCELLED':
      return 'danger';
    default:
      return null;
  }
};

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

// Navegação
const viewReservationDetails = (reservation) => {
  router.push(`/reservations/${reservation.id}`);
};

const goToRoom = (roomId) => {
  router.push(`/rooms/${roomId}`);
};

const createNewReservation = () => {
  router.push('/reservations');
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
