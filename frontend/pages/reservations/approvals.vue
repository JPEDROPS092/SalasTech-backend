<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Data
const pendingReservations = ref([]);
const loading = ref(false);
const totalRecords = ref(0);

// Selected reservation for operations
const selectedReservation = ref(null);

// Filters
const filters = reactive({
  global: { value: null, matchMode: 'contains' },
  title: { value: null, matchMode: 'contains' },
  room: { value: null, matchMode: 'contains' },
  user: { value: null, matchMode: 'contains' }
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
const approveDialog = ref(false);
const rejectDialog = ref(false);
const detailsDialog = ref(false);

// Rejection reason
const rejectionReason = ref('');

// Check if user has admin access
const checkAdminAccess = () => {
  if (!auth.isAuthenticated || !auth.hasAdminAccess) {
    toast.add({
      severity: 'error',
      summary: 'Acesso Negado',
      detail: 'Você não tem permissão para acessar esta página',
      life: 3000
    });
    router.push('/dashboard');
    return false;
  }
  return true;
};

// Fetch pending reservations
const loadPendingReservations = async () => {
  if (!checkAdminAccess()) return;

  try {
    loading.value = true;
    
    // Implement API call to get pending reservations with pagination
    // const response = await api.getPendingReservations(lazyParams.value);
    // pendingReservations.value = response.data;
    // totalRecords.value = response.total;
    
    // Mock data for now
    setTimeout(() => {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const nextWeek = new Date(today);
      nextWeek.setDate(nextWeek.getDate() + 7);
      
      pendingReservations.value = [
        {
          id: 3,
          title: 'Palestra: Inteligência Artificial',
          description: 'Palestra sobre avanços em IA e suas aplicações',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 3 * 60 * 60 * 1000).toISOString(),
          room_id: 3,
          room: 'Auditório',
          user: 'Roberto Mendes',
          user_id: 3,
          user_email: 'roberto.mendes@ifam.edu.br',
          status: 'PENDING',
          created_at: today.toISOString()
        },
        {
          id: 4,
          title: 'Reunião de Coordenação',
          description: 'Reunião mensal de coordenação de cursos',
          start_time: nextWeek.toISOString(),
          end_time: new Date(nextWeek.getTime() + 1.5 * 60 * 60 * 1000).toISOString(),
          room_id: 4,
          room: 'Sala de Reuniões',
          user: 'Maria Santos',
          user_id: 4,
          user_email: 'maria.santos@ifam.edu.br',
          status: 'PENDING',
          created_at: today.toISOString()
        },
        {
          id: 6,
          title: 'Defesa de TCC',
          description: 'Defesa de Trabalho de Conclusão de Curso do aluno José Silva',
          start_time: nextWeek.toISOString(),
          end_time: new Date(nextWeek.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 3,
          room: 'Auditório',
          user: 'Ana Oliveira',
          user_id: 6,
          user_email: 'ana.oliveira@ifam.edu.br',
          status: 'PENDING',
          created_at: new Date(today.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 7,
          title: 'Aula de Física',
          description: 'Aula de Física Mecânica para turma de Engenharia',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 5,
          room: 'Sala 102',
          user: 'Paulo Ferreira',
          user_id: 7,
          user_email: 'paulo.ferreira@ifam.edu.br',
          status: 'PENDING',
          created_at: new Date(today.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 8,
          title: 'Workshop de Programação',
          description: 'Workshop de Python para iniciantes',
          start_time: nextWeek.toISOString(),
          end_time: new Date(nextWeek.getTime() + 4 * 60 * 60 * 1000).toISOString(),
          room_id: 2,
          room: 'Laboratório de Informática',
          user: 'Carla Mendes',
          user_id: 8,
          user_email: 'carla.mendes@ifam.edu.br',
          status: 'PENDING',
          created_at: today.toISOString()
        }
      ];
      
      totalRecords.value = 5;
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error loading pending reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as reservas pendentes',
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
  loadPendingReservations();
};

// Handle sort
const onSort = (event) => {
  lazyParams.value.sortField = event.sortField;
  lazyParams.value.sortOrder = event.sortOrder;
  loadPendingReservations();
};

// Handle filter
const onFilter = () => {
  lazyParams.value.first = 0;
  lazyParams.value.page = 1;
  loadPendingReservations();
};

// Open approval dialog
const openApproveDialog = (reservation) => {
  selectedReservation.value = reservation;
  approveDialog.value = true;
};

// Open rejection dialog
const openRejectDialog = (reservation) => {
  selectedReservation.value = reservation;
  rejectionReason.value = '';
  rejectDialog.value = true;
};

// Open details dialog
const openDetailsDialog = (reservation) => {
  selectedReservation.value = reservation;
  detailsDialog.value = true;
};

// Approve reservation
const approveReservation = async () => {
  try {
    // Implement API call to approve reservation
    // await api.updateReservation(selectedReservation.value.id, { status: 'CONFIRMED' });
    
    // Update local data
    pendingReservations.value = pendingReservations.value.filter(r => r.id !== selectedReservation.value.id);
    totalRecords.value--;
    
    approveDialog.value = false;
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva aprovada com sucesso',
      life: 3000
    });
  } catch (error) {
    console.error('Error approving reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível aprovar a reserva',
      life: 3000
    });
  }
};

// Reject reservation
const rejectReservation = async () => {
  if (!rejectionReason.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Por favor, forneça um motivo para a rejeição',
      life: 3000
    });
    return;
  }
  
  try {
    // Implement API call to reject reservation
    // await api.updateReservation(selectedReservation.value.id, { 
    //   status: 'CANCELLED',
    //   rejection_reason: rejectionReason.value
    // });
    
    // Update local data
    pendingReservations.value = pendingReservations.value.filter(r => r.id !== selectedReservation.value.id);
    totalRecords.value--;
    
    rejectDialog.value = false;
    rejectionReason.value = '';
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva rejeitada com sucesso',
      life: 3000
    });
  } catch (error) {
    console.error('Error rejecting reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível rejeitar a reserva',
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

// Format relative time (e.g., "2 days ago")
const formatRelativeTime = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffDays > 0) {
    return `${diffDays} dia${diffDays > 1 ? 's' : ''} atrás`;
  } else if (diffHours > 0) {
    return `${diffHours} hora${diffHours > 1 ? 's' : ''} atrás`;
  } else if (diffMins > 0) {
    return `${diffMins} minuto${diffMins > 1 ? 's' : ''} atrás`;
  } else {
    return 'Agora mesmo';
  }
};

// Check for room conflicts
const checkRoomConflicts = async (reservation) => {
  try {
    // Implement API call to check for conflicts
    // const conflicts = await api.checkRoomConflicts(reservation.room_id, reservation.start_time, reservation.end_time, reservation.id);
    // return conflicts;
    
    // Mock data for now
    // For demo purposes, let's say there's a conflict for room 3 (Auditório)
    if (reservation.room_id === 3) {
      return [
        {
          id: 10,
          title: 'Evento Existente',
          start_time: reservation.start_time,
          end_time: reservation.end_time,
          status: 'CONFIRMED'
        }
      ];
    }
    
    return [];
  } catch (error) {
    console.error('Error checking conflicts:', error);
    return [];
  }
};

// Initialize component
onMounted(async () => {
  if (checkAdminAccess()) {
    await loadPendingReservations();
  }
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <Toast />
        
        <div class="flex justify-content-between align-items-center mb-4">
          <h5 class="m-0">Aprovação de Reservas</h5>
          <div>
            <Button icon="pi pi-refresh" class="p-button-outlined" @click="loadPendingReservations" :loading="loading" />
          </div>
        </div>
        
        <DataTable 
          :value="pendingReservations" 
          dataKey="id"
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} reservas pendentes"
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
          emptyMessage="Não há reservas pendentes de aprovação"
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
          
          <Column field="user" header="Solicitante" :sortable="true" style="min-width: 10rem">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por solicitante" class="p-column-filter" />
            </template>
          </Column>
          
          <Column field="start_time" header="Início" :sortable="true" style="min-width: 10rem">
            <template #body="{ data }">
              {{ formatDate(data.start_time) }}
            </template>
          </Column>
          
          <Column field="created_at" header="Solicitado" :sortable="true" style="min-width: 8rem">
            <template #body="{ data }">
              {{ formatRelativeTime(data.created_at) }}
            </template>
          </Column>
          
          <Column header="Ações" style="min-width: 15rem">
            <template #body="{ data }">
              <div class="flex">
                <Button icon="pi pi-info-circle" class="p-button-rounded p-button-text p-button-info mr-2" @click="openDetailsDialog(data)" />
                <Button icon="pi pi-check" class="p-button-rounded p-button-text p-button-success mr-2" @click="openApproveDialog(data)" />
                <Button icon="pi pi-times" class="p-button-rounded p-button-text p-button-danger mr-2" @click="openRejectDialog(data)" />
                <Button icon="pi pi-map" class="p-button-rounded p-button-text p-button-secondary" @click="viewRoom(data.room_id)" />
              </div>
            </template>
          </Column>
        </DataTable>
        
        <!-- Approve Reservation Dialog -->
        <Dialog v-model:visible="approveDialog" :style="{width: '450px'}" header="Aprovar Reserva" :modal="true">
          <div v-if="selectedReservation" class="confirmation-content">
            <i class="pi pi-check-circle mr-3" style="font-size: 2rem; color: var(--green-500)" />
            <div>
              <p>Tem certeza que deseja aprovar a reserva:</p>
              <p class="font-bold">{{ selectedReservation.title }}</p>
              <p>Sala: {{ selectedReservation.room }}</p>
              <p>Data: {{ formatDate(selectedReservation.start_time) }}</p>
              <p>Solicitante: {{ selectedReservation.user }}</p>
            </div>
          </div>
          <template #footer>
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="approveDialog = false" />
            <Button label="Aprovar" icon="pi pi-check" class="p-button-text p-button-success" @click="approveReservation" />
          </template>
        </Dialog>
        
        <!-- Reject Reservation Dialog -->
        <Dialog v-model:visible="rejectDialog" :style="{width: '450px'}" header="Rejeitar Reserva" :modal="true">
          <div v-if="selectedReservation" class="p-fluid">
            <div class="confirmation-content mb-4">
              <i class="pi pi-times-circle mr-3" style="font-size: 2rem; color: var(--red-500)" />
              <div>
                <p>Tem certeza que deseja rejeitar a reserva:</p>
                <p class="font-bold">{{ selectedReservation.title }}</p>
                <p>Sala: {{ selectedReservation.room }}</p>
                <p>Data: {{ formatDate(selectedReservation.start_time) }}</p>
                <p>Solicitante: {{ selectedReservation.user }}</p>
              </div>
            </div>
            
            <div class="field">
              <label for="rejectionReason">Motivo da Rejeição</label>
              <Textarea id="rejectionReason" v-model="rejectionReason" rows="3" placeholder="Informe o motivo da rejeição" />
              <small class="text-muted">O motivo será enviado ao solicitante.</small>
            </div>
          </div>
          <template #footer>
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="rejectDialog = false" />
            <Button label="Rejeitar" icon="pi pi-check" class="p-button-text p-button-danger" @click="rejectReservation" />
          </template>
        </Dialog>
        
        <!-- Reservation Details Dialog -->
        <Dialog v-model:visible="detailsDialog" :style="{width: '650px'}" header="Detalhes da Reserva" :modal="true">
          <div v-if="selectedReservation" class="reservation-details">
            <div class="grid">
              <div class="col-12">
                <h4>{{ selectedReservation.title }}</h4>
                <p>{{ selectedReservation.description }}</p>
              </div>
              
              <div class="col-12 md:col-6">
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
                  <label class="col-12 md:col-4 font-bold">Solicitado:</label>
                  <div class="col-12 md:col-8">{{ formatRelativeTime(selectedReservation.created_at) }}</div>
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Solicitante:</label>
                  <div class="col-12 md:col-8">{{ selectedReservation.user }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Email:</label>
                  <div class="col-12 md:col-8">{{ selectedReservation.user_email }}</div>
                </div>
              </div>
              
              <div class="col-12">
                <Divider />
                <h5>Verificação de Conflitos</h5>
                <ProgressSpinner v-if="loading" style="width: 50px; height: 50px" class="my-3" />
                <div v-else>
                  <div v-if="selectedReservation.room_id === 3" class="p-message p-message-warn mb-3">
                    <div class="p-message-wrapper">
                      <span class="p-message-icon pi pi-exclamation-triangle"></span>
                      <div class="p-message-text">
                        <strong>Atenção:</strong> Existe um conflito com outra reserva para esta sala no mesmo horário.
                      </div>
                    </div>
                  </div>
                  <div v-else class="p-message p-message-success mb-3">
                    <div class="p-message-wrapper">
                      <span class="p-message-icon pi pi-check"></span>
                      <div class="p-message-text">
                        <strong>Sala disponível:</strong> Não há conflitos para esta sala no horário solicitado.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <template #footer>
            <Button label="Fechar" icon="pi pi-times" class="p-button-text" @click="detailsDialog = false" />
            <Button label="Rejeitar" icon="pi pi-times" class="p-button-text p-button-danger" @click="() => { detailsDialog = false; openRejectDialog(selectedReservation); }" />
            <Button label="Aprovar" icon="pi pi-check" class="p-button-text p-button-success" @click="() => { detailsDialog = false; openApproveDialog(selectedReservation); }" />
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

.p-column-filter {
  width: 100%;
}

.confirmation-content {
  display: flex;
  align-items: flex-start;
}

.field.grid {
  margin: 0;
}

h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: var(--text-color);
  font-weight: 600;
}

h5 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color-secondary);
  font-weight: 600;
}

.p-message {
  border-radius: 6px;
  padding: 1rem;
}
</style>
