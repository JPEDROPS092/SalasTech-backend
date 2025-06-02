<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const route = useRoute();
const router = useRouter();
const toast = useToast();

// Reservation ID from route
const reservationId = computed(() => route.params.id as string);

// Reservation data
const reservation = ref(null);
const loading = ref(true);

// Dialog visibility
const cancelDialog = ref(false);
const editDialog = ref(false);

// Edit form
const editForm = ref({
  title: '',
  description: '',
  status: ''
});

// Status options
const statusOptions = ref([
  { label: 'Confirmada', value: 'CONFIRMED' },
  { label: 'Pendente', value: 'PENDING' },
  { label: 'Cancelada', value: 'CANCELLED' }
]);

// Validation
const submitted = ref(false);

// Fetch reservation data
const fetchReservation = async () => {
  try {
    loading.value = true;
    
    // Implement API call to get reservation by ID
    // const response = await api.getReservation(reservationId.value);
    // reservation.value = response;
    
    // Mock data for now
    setTimeout(() => {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const nextWeek = new Date(today);
      nextWeek.setDate(nextWeek.getDate() + 7);
      
      if (reservationId.value === '1') {
        reservation.value = {
          id: 1,
          title: 'Aula de Matemática',
          description: 'Aula de Cálculo I para turma de Engenharia. Conteúdo: Limites e Derivadas. Trazer calculadora científica.',
          start_time: today.toISOString(),
          end_time: new Date(today.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: {
            id: 1,
            name: 'Sala 101',
            capacity: 40,
            department: 'Departamento Acadêmico',
            location: 'Bloco A, 1º Andar'
          },
          user: {
            id: 1,
            name: 'Carlos Silva',
            email: 'carlos.silva@ifam.edu.br',
            role: 'PROFESSOR'
          },
          status: 'CONFIRMED',
          created_at: yesterday.toISOString(),
          updated_at: yesterday.toISOString()
        };
      } else if (reservationId.value === '2') {
        reservation.value = {
          id: 2,
          title: 'Aula de Programação',
          description: 'Aula de Programação Web para turma de Sistemas de Informação. Conteúdo: JavaScript e DOM.',
          start_time: yesterday.toISOString(),
          end_time: new Date(yesterday.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 2,
          room: {
            id: 2,
            name: 'Laboratório de Informática',
            capacity: 30,
            department: 'Departamento de TI',
            location: 'Bloco B, Térreo'
          },
          user: {
            id: 2,
            name: 'João Pereira',
            email: 'joao.pereira@ifam.edu.br',
            role: 'PROFESSOR'
          },
          status: 'CONFIRMED',
          created_at: new Date(yesterday.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(yesterday.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString()
        };
      } else if (reservationId.value === '3') {
        reservation.value = {
          id: 3,
          title: 'Palestra: Inteligência Artificial',
          description: 'Palestra sobre avanços em IA e suas aplicações. Palestrante: Dr. Roberto Mendes, pesquisador da área de Machine Learning.',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 3 * 60 * 60 * 1000).toISOString(),
          room_id: 3,
          room: {
            id: 3,
            name: 'Auditório',
            capacity: 120,
            department: 'Departamento Administrativo',
            location: 'Bloco Central, Térreo'
          },
          user: {
            id: 3,
            name: 'Roberto Mendes',
            email: 'roberto.mendes@ifam.edu.br',
            role: 'PROFESSOR'
          },
          status: 'PENDING',
          created_at: yesterday.toISOString(),
          updated_at: yesterday.toISOString()
        };
      } else if (reservationId.value === '4') {
        reservation.value = {
          id: 4,
          title: 'Reunião de Coordenação',
          description: 'Reunião mensal de coordenação de cursos. Pauta: Planejamento do próximo semestre, avaliação de professores, orçamento.',
          start_time: nextWeek.toISOString(),
          end_time: new Date(nextWeek.getTime() + 1.5 * 60 * 60 * 1000).toISOString(),
          room_id: 4,
          room: {
            id: 4,
            name: 'Sala de Reuniões',
            capacity: 15,
            department: 'Departamento Administrativo',
            location: 'Bloco Administrativo, 2º Andar'
          },
          user: {
            id: 4,
            name: 'Maria Santos',
            email: 'maria.santos@ifam.edu.br',
            role: 'COORDENADOR'
          },
          status: 'PENDING',
          created_at: yesterday.toISOString(),
          updated_at: yesterday.toISOString()
        };
      } else if (reservationId.value === '5') {
        reservation.value = {
          id: 5,
          title: 'Monitoria de Matemática',
          description: 'Monitoria para alunos com dificuldade em Cálculo. Foco em exercícios práticos e resolução de problemas.',
          start_time: tomorrow.toISOString(),
          end_time: new Date(tomorrow.getTime() + 2 * 60 * 60 * 1000).toISOString(),
          room_id: 1,
          room: {
            id: 1,
            name: 'Sala 101',
            capacity: 40,
            department: 'Departamento Acadêmico',
            location: 'Bloco A, 1º Andar'
          },
          user: {
            id: 5,
            name: 'Pedro Santos',
            email: 'pedro.santos@ifam.edu.br',
            role: 'MONITOR'
          },
          status: 'CANCELLED',
          created_at: yesterday.toISOString(),
          updated_at: today.toISOString()
        };
      } else {
        // If reservation not found, show error and redirect
        toast.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Reserva não encontrada',
          life: 3000
        });
        router.push('/reservations');
      }
      
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error fetching reservation:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar os dados da reserva',
      life: 3000
    });
    loading.value = false;
    router.push('/reservations');
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

// Check if user can edit reservation
const canEditReservation = computed(() => {
  if (!reservation.value || !auth.user) return false;
  
  // In a real app, you would check if the user is the owner or has admin rights
  return auth.hasAdminAccess || (reservation.value.user.id === auth.user.id);
});

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
