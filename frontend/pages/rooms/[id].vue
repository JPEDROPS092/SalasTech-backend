<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const route = useRoute();
const router = useRouter();
const toast = useToast();

// Room ID from route
const roomId = computed(() => route.params.id as string);

// Room data
const room = ref(null);
const loading = ref(true);
const reservations = ref([]);
const loadingReservations = ref(true);

// Resources options (for display)
const resourceOptions = ref([
  { name: 'Projetor', id: 1, icon: 'pi pi-desktop' },
  { name: 'Computador', id: 2, icon: 'pi pi-desktop' },
  { name: 'Ar Condicionado', id: 3, icon: 'pi pi-sun' },
  { name: 'Smart TV', id: 4, icon: 'pi pi-desktop' },
  { name: 'Sistema de Som', id: 5, icon: 'pi pi-volume-up' },
  { name: 'Quadro Branco', id: 6, icon: 'pi pi-pencil' },
  { name: 'Mesa de Reunião', id: 7, icon: 'pi pi-users' }
]);

// Fetch room data
const fetchRoom = async () => {
  try {
    loading.value = true;
    
    // Implement API call to get room by ID
    // const response = await api.getRoom(roomId.value);
    // room.value = response;
    
    // Mock data for now
    setTimeout(() => {
      if (roomId.value === '1') {
        room.value = { 
          id: 1, 
          name: 'Sala 101', 
          description: 'Sala de aula padrão com capacidade para 40 alunos. Equipada com projetor, ar condicionado e quadro branco. Localizada no primeiro andar do bloco A.',
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'AVAILABLE',
          location: 'Bloco A, 1º Andar',
          created_at: '2023-01-15T10:30:00',
          updated_at: '2023-06-20T14:45:00'
        };
      } else if (roomId.value === '2') {
        room.value = { 
          id: 2, 
          name: 'Laboratório de Informática', 
          description: 'Laboratório com 30 computadores para aulas práticas de programação e design. Equipado com projetores, computadores, ar condicionado e smart TV.',
          capacity: 30, 
          department: 'Departamento de TI',
          department_id: 1,
          resources: [1, 2, 3, 4],
          status: 'OCCUPIED',
          location: 'Bloco B, Térreo',
          created_at: '2023-02-10T09:15:00',
          updated_at: '2023-07-05T11:20:00'
        };
      } else if (roomId.value === '3') {
        room.value = { 
          id: 3, 
          name: 'Auditório', 
          description: 'Auditório principal para eventos, palestras e apresentações. Equipado com sistema de som, projetor, ar condicionado e smart TV.',
          capacity: 120, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 3, 4, 5],
          status: 'AVAILABLE',
          location: 'Bloco Central, Térreo',
          created_at: '2023-01-05T08:00:00',
          updated_at: '2023-08-12T16:30:00'
        };
      } else if (roomId.value === '4') {
        room.value = { 
          id: 4, 
          name: 'Sala de Reuniões', 
          description: 'Sala para reuniões e videoconferências com mesa oval para 15 pessoas. Equipada com projetor, computador, ar condicionado, smart TV e mesa de reunião.',
          capacity: 15, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 2, 3, 4, 7],
          status: 'AVAILABLE',
          location: 'Bloco Administrativo, 2º Andar',
          created_at: '2023-03-20T13:45:00',
          updated_at: '2023-07-18T10:10:00'
        };
      } else if (roomId.value === '5') {
        room.value = { 
          id: 5, 
          name: 'Sala 102', 
          description: 'Sala de aula padrão com capacidade para 40 alunos. Equipada com projetor, ar condicionado e quadro branco. Localizada no primeiro andar do bloco A.',
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'MAINTENANCE',
          location: 'Bloco A, 1º Andar',
          created_at: '2023-01-15T10:35:00',
          updated_at: '2023-09-01T09:00:00'
        };
      } else {
        // If room not found, show error and redirect
        toast.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Sala não encontrada',
          life: 3000
        });
        router.push('/rooms');
      }
      
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error fetching room:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar os dados da sala',
      life: 3000
    });
    loading.value = false;
    router.push('/rooms');
  }
};

// Fetch upcoming reservations for this room
const fetchReservations = async () => {
  try {
    loadingReservations.value = true;
    
    // Implement API call to get upcoming reservations for this room
    // const response = await api.getRoomReservations(roomId.value);
    // reservations.value = response;
    
    // Mock data for now
    setTimeout(() => {
      if (roomId.value === '1') {
        reservations.value = [
          {
            id: 101,
            title: 'Aula de Matemática',
            start_time: '2023-10-25T08:00:00',
            end_time: '2023-10-25T10:00:00',
            user: 'Prof. Carlos Silva',
            status: 'CONFIRMED'
          },
          {
            id: 102,
            title: 'Aula de Física',
            start_time: '2023-10-25T14:00:00',
            end_time: '2023-10-25T16:00:00',
            user: 'Prof. Ana Oliveira',
            status: 'CONFIRMED'
          }
        ];
      } else if (roomId.value === '2') {
        reservations.value = [
          {
            id: 201,
            title: 'Aula de Programação',
            start_time: '2023-10-24T10:00:00',
            end_time: '2023-10-24T12:00:00',
            user: 'Prof. João Pereira',
            status: 'CONFIRMED'
          },
          {
            id: 202,
            title: 'Curso de Web Design',
            start_time: '2023-10-25T08:00:00',
            end_time: '2023-10-25T12:00:00',
            user: 'Prof. Mariana Costa',
            status: 'CONFIRMED'
          },
          {
            id: 203,
            title: 'Laboratório de Redes',
            start_time: '2023-10-26T14:00:00',
            end_time: '2023-10-26T18:00:00',
            user: 'Prof. Ricardo Almeida',
            status: 'PENDING'
          }
        ];
      } else {
        reservations.value = [];
      }
      
      loadingReservations.value = false;
    }, 700);
  } catch (error) {
    console.error('Error fetching reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as reservas',
      life: 3000
    });
    loadingReservations.value = false;
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
    case 'AVAILABLE':
      return 'success';
    case 'OCCUPIED':
      return 'warning';
    case 'MAINTENANCE':
      return 'danger';
    default:
      return 'info';
  }
};

// Get status label
const getStatusLabel = (status) => {
  switch (status) {
    case 'AVAILABLE':
      return 'Disponível';
    case 'OCCUPIED':
      return 'Ocupada';
    case 'MAINTENANCE':
      return 'Em Manutenção';
    default:
      return status;
  }
};

// Get reservation status severity
const getReservationStatusSeverity = (status) => {
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

// Navigate to edit room
const editRoom = () => {
  router.push(`/rooms/${roomId.value}/edit`);
};

// Navigate to room calendar
const viewCalendar = () => {
  router.push(`/rooms/${roomId.value}/calendar`);
};

// Create new reservation for this room
const createReservation = () => {
  router.push({
    path: '/reservations/new',
    query: { roomId: roomId.value }
  });
};

// View reservation details
const viewReservation = (reservationId) => {
  router.push(`/reservations/${reservationId}`);
};

// Initialize component
onMounted(async () => {
  await fetchRoom();
  await fetchReservations();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <Toast />
      
      <div v-if="loading" class="card flex justify-content-center">
        <ProgressSpinner />
      </div>
      
      <div v-else-if="room" class="grid">
        <!-- Room Details Card -->
        <div class="col-12 lg:col-8">
          <div class="card">
            <div class="flex justify-content-between align-items-center mb-4">
              <div class="flex align-items-center">
                <h2 class="m-0">{{ room.name }}</h2>
                <Tag :value="getStatusLabel(room.status)" :severity="getStatusSeverity(room.status)" class="ml-3" />
              </div>
              <div>
                <Button icon="pi pi-calendar" label="Ver Calendário" class="p-button-info mr-2" @click="viewCalendar" />
                <Button icon="pi pi-pencil" label="Editar" class="p-button-warning mr-2" @click="editRoom" v-if="auth.hasAdminAccess" />
                <Button icon="pi pi-plus" label="Reservar" class="p-button-success" @click="createReservation" />
              </div>
            </div>
            
            <div class="grid">
              <div class="col-12">
                <h4>Descrição</h4>
                <p>{{ room.description }}</p>
              </div>
              
              <div class="col-12 md:col-6">
                <h4>Detalhes</h4>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Capacidade:</label>
                  <div class="col-12 md:col-8">{{ room.capacity }} pessoas</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Departamento:</label>
                  <div class="col-12 md:col-8">{{ room.department }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Localização:</label>
                  <div class="col-12 md:col-8">{{ room.location }}</div>
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <h4>Informações Adicionais</h4>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Criado em:</label>
                  <div class="col-12 md:col-8">{{ formatDate(room.created_at) }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">Atualizado em:</label>
                  <div class="col-12 md:col-8">{{ formatDate(room.updated_at) }}</div>
                </div>
                <div class="field grid mb-2">
                  <label class="col-12 md:col-4 font-bold">ID:</label>
                  <div class="col-12 md:col-8">{{ room.id }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Resources Card -->
        <div class="col-12 lg:col-4">
          <div class="card">
            <h3>Recursos Disponíveis</h3>
            <div v-if="room.resources && room.resources.length > 0">
              <ul class="resource-list p-0 m-0">
                <li v-for="resourceId in room.resources" :key="resourceId" class="flex align-items-center mb-3">
                  <i :class="resourceOptions.find(r => r.id === resourceId)?.icon || 'pi pi-check'" class="mr-2 text-xl"></i>
                  <span>{{ resourceOptions.find(r => r.id === resourceId)?.name }}</span>
                </li>
              </ul>
            </div>
            <div v-else class="p-3 surface-200 border-round">
              <i class="pi pi-info-circle mr-2"></i>
              <span>Nenhum recurso cadastrado</span>
            </div>
          </div>
        </div>
        
        <!-- Upcoming Reservations Card -->
        <div class="col-12">
          <div class="card">
            <div class="flex justify-content-between align-items-center mb-3">
              <h3 class="m-0">Próximas Reservas</h3>
              <Button icon="pi pi-calendar-plus" label="Nova Reserva" @click="createReservation" />
            </div>
            
            <div v-if="loadingReservations" class="flex justify-content-center">
              <ProgressSpinner style="width: 50px; height: 50px" />
            </div>
            
            <div v-else-if="reservations.length > 0">
              <DataTable :value="reservations" responsiveLayout="scroll" stripedRows>
                <Column field="title" header="Título"></Column>
                <Column field="start_time" header="Início">
                  <template #body="{ data }">
                    {{ formatDate(data.start_time) }}
                  </template>
                </Column>
                <Column field="end_time" header="Término">
                  <template #body="{ data }">
                    {{ formatDate(data.end_time) }}
                  </template>
                </Column>
                <Column field="user" header="Responsável"></Column>
                <Column field="status" header="Status">
                  <template #body="{ data }">
                    <Tag :value="data.status" :severity="getReservationStatusSeverity(data.status)" />
                  </template>
                </Column>
                <Column header="Ações">
                  <template #body="{ data }">
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info" @click="viewReservation(data.id)" />
                  </template>
                </Column>
              </DataTable>
            </div>
            
            <div v-else class="p-4 surface-200 border-round text-center">
              <i class="pi pi-calendar-times text-xl mb-3 block"></i>
              <p class="m-0">Não há reservas agendadas para esta sala.</p>
              <Button label="Criar Reserva" icon="pi pi-plus" class="p-button-outlined mt-3" @click="createReservation" />
            </div>
          </div>
        </div>
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

.resource-list {
  list-style-type: none;
}

.resource-list li i {
  color: var(--primary-color);
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
</style>
