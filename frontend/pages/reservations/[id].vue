<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'nuxt/app';
import { useReservationStore } from '~/stores/reservation';
import { useRoomStore } from '~/stores/room';
import { useAuth } from '~/composables/use-auth';
import { useToast } from 'primevue/usetoast';

// Definir metadados da página
definePageMeta({
  middleware: ['auth'],
  public: false
});

// Composables
const auth = useAuth();
const toast = useToast();
const route = useRoute();
const router = useRouter();
const reservationStore = useReservationStore();
const roomStore = useRoomStore();

// Estado
const loading = ref(true);
const editDialog = ref(false);
const cancelDialog = ref(false);
const submitted = ref(false);

// Formulário de edição
const editForm = ref({
  id: null,
  title: '',
  description: '',
  start_time: null,
  end_time: null,
  room_id: null,
  status: 'PENDING'
});

// Computed
const isAdmin = computed(() => auth.isAdmin);
const isAuthenticated = computed(() => auth.isAuthenticated);
const reservation = computed(() => reservationStore.currentReservation);
const rooms = computed(() => roomStore.rooms);

const isOwner = computed(() => {
  if (!auth.user || !reservation.value) return false;
  return auth.user.id === reservation.value.user?.id;
});

const canEdit = computed(() => {
  if (!reservation.value) return false;
  return isAdmin.value || (isOwner.value && reservation.value.status === 'PENDING');
});

const canCancel = computed(() => {
  if (!reservation.value) return false;
  return isAdmin.value || (isOwner.value && reservation.value.status === 'CONFIRMED');
});

// Carregar dados da reserva
const fetchReservation = async () => {
  loading.value = true;
  try {
    const id = route.params.id;
    
    // Carregar detalhes da reserva
    await reservationStore.fetchReservation(id);
    
    // Carregar salas para o formulário se ainda não foram carregadas
    if (rooms.value.length === 0) {
      await roomStore.fetchRooms(1, 100);
    }
    
    if (!reservation.value) {
      toast.add({ severity: 'error', summary: 'Erro', detail: 'Reserva não encontrada', life: 3000 });
      router.push('/reservations');
    }
  } catch (error) {
    console.error('Erro ao carregar detalhes da reserva:', error);
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível carregar os detalhes da reserva', life: 3000 });
    router.push('/reservations');
  } finally {
    loading.value = false;
  }
};

// Abrir diálogo de edição
// Check if reservation can be cancelled
const canCancelReservation = computed(() => {
  if (!reservation.value) return false;
  
  // Can only cancel if status is not already cancelled
  return canEditReservation.value && reservation.value.status !== 'CANCELLED';
});

// Open edit dialog
const openEditDialog = () => {
  editForm.value = {
    title: reservation.value.title,
    description: reservation.value.description,
    status: reservation.value.status
  };
  
  editDialog.value = true;
};

// Save edited reservation
const saveEdit = async () => {
  submitted.value = true;
  
  if (!editForm.value.title.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'O título é obrigatório',
      life: 3000
    });
    return;
  }
  
  try {
    // Implement API call to update reservation
    // await api.updateReservation(reservationId.value, {
    //   title: editForm.value.title,
    //   description: editForm.value.description,
    //   status: editForm.value.status
    // });
    
    // Update local data
    reservation.value = {
      ...reservation.value,
      title: editForm.value.title,
      description: editForm.value.description,
      status: editForm.value.status,
      updated_at: new Date().toISOString()
    };
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva atualizada com sucesso',
      life: 3000
    });
    
    editDialog.value = false;
    submitted.value = false;
  } catch (error) {
    console.error('Error updating reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível atualizar a reserva',
      life: 3000
    });
  }
};

// Cancel reservation
const cancelReservation = async () => {
  try {
    // Implement API call to cancel reservation
    // await api.updateReservation(reservationId.value, {
    //   status: 'CANCELLED'
    // });
    
    // Update local data
    reservation.value = {
      ...reservation.value,
      status: 'CANCELLED',
      updated_at: new Date().toISOString()
    };
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Reserva cancelada com sucesso',
      life: 3000
    });
    
    cancelDialog.value = false;
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

// View room details
const viewRoom = () => {
  if (reservation.value && reservation.value.room_id) {
    router.push(`/rooms/${reservation.value.room_id}`);
  }
};

// Initialize component
onMounted(async () => {
  await fetchReservation();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <Toast />
      
      <div v-if="loading" class="card flex justify-content-center">
        <ProgressSpinner />
      </div>
      
      <div v-else-if="reservation" class="grid">
        <!-- Reservation Details Card -->
        <div class="col-12">
          <div class="card">
            <div class="flex justify-content-between align-items-center mb-4">
              <div class="flex align-items-center">
                <h2 class="m-0">{{ reservation.title }}</h2>
                <Tag :value="getStatusLabel(reservation.status)" :severity="getStatusSeverity(reservation.status)" class="ml-3" />
              </div>
              <div>
                <Button icon="pi pi-pencil" label="Editar" class="p-button-warning mr-2" @click="openEditDialog" v-if="canEditReservation" />
                <Button icon="pi pi-times" label="Cancelar Reserva" class="p-button-danger" @click="cancelDialog = true" v-if="canCancelReservation" />
              </div>
            </div>
            
            <div class="grid">
              <div class="col-12">
                <h4>Descrição</h4>
                <p>{{ reservation.description }}</p>
              </div>
              
              <div class="col-12 md:col-6">
                <h4>Detalhes da Reserva</h4>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Data e Hora de Início:</label>
                  <div class="col-12 md:col-8">{{ formatDate(reservation.start_time) }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Data e Hora de Término:</label>
                  <div class="col-12 md:col-8">{{ formatDate(reservation.end_time) }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Status:</label>
                  <div class="col-12 md:col-8">
                    <Tag :value="getStatusLabel(reservation.status)" :severity="getStatusSeverity(reservation.status)" />
                  </div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Criado em:</label>
                  <div class="col-12 md:col-8">{{ formatDate(reservation.created_at) }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Atualizado em:</label>
                  <div class="col-12 md:col-8">{{ formatDate(reservation.updated_at) }}</div>
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <h4>Informações da Sala</h4>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Nome:</label>
                  <div class="col-12 md:col-8">
                    <Button 
                      :label="reservation.room.name" 
                      class="p-button-link p-0" 
                      @click="viewRoom" 
                    />
                  </div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Capacidade:</label>
                  <div class="col-12 md:col-8">{{ reservation.room.capacity }} pessoas</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Departamento:</label>
                  <div class="col-12 md:col-8">{{ reservation.room.department }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Localização:</label>
                  <div class="col-12 md:col-8">{{ reservation.room.location }}</div>
                </div>
              </div>
              
              <div class="col-12">
                <h4>Responsável</h4>
                <div class="flex align-items-center">
                  <Avatar :label="reservation.user.name.charAt(0)" class="mr-2" style="background-color: var(--primary-color); color: var(--primary-color-text)" />
                  <div>
                    <div class="font-bold">{{ reservation.user.name }}</div>
                    <div>{{ reservation.user.email }}</div>
                    <Tag :value="reservation.user.role" severity="info" class="mt-2" />
                  </div>
                </div>
              </div>
            </div>
            
            <div class="flex justify-content-end mt-4">
              <Button icon="pi pi-arrow-left" label="Voltar para Lista" class="p-button-outlined" @click="router.push('/reservations')" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Cancel Reservation Dialog -->
      <Dialog v-model:visible="cancelDialog" :style="{width: '450px'}" header="Cancelar Reserva" :modal="true">
        <div class="confirmation-content">
          <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
          <span>Tem certeza que deseja cancelar esta reserva?</span>
        </div>
        <template #footer>
          <Button label="Não" icon="pi pi-times" class="p-button-text" @click="cancelDialog = false" />
          <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="cancelReservation" />
        </template>
      </Dialog>
      
      <!-- Edit Reservation Dialog -->
      <Dialog v-model:visible="editDialog" :style="{width: '550px'}" header="Editar Reserva" :modal="true" class="p-fluid">
        <div class="field">
          <label for="title">Título</label>
          <InputText id="title" v-model="editForm.title" required autofocus :class="{'p-invalid': submitted && !editForm.title}" />
          <small class="p-error" v-if="submitted && !editForm.title">Título é obrigatório.</small>
        </div>
        
        <div class="field">
          <label for="description">Descrição</label>
          <Textarea id="description" v-model="editForm.description" rows="3" />
        </div>
        
        <div class="field" v-if="auth.hasAdminAccess">
          <label for="status">Status</label>
          <Dropdown id="status" v-model="editForm.status" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Selecione um status" />
        </div>
        
        <template #footer>
          <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="editDialog = false" />
          <Button label="Salvar" icon="pi pi-check" class="p-button-text" @click="saveEdit" />
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

h4 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-color-secondary);
  font-weight: 600;
}

.field.grid {
  margin: 0;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
