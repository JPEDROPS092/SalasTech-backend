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

// Calendar options
const calendarOptions = ref({
  initialView: 'timeGridWeek',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  editable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  allDaySlot: false,
  slotMinTime: '07:00:00',
  slotMaxTime: '22:00:00',
  slotDuration: '00:30:00',
  locale: 'pt-br',
  buttonText: {
    today: 'Hoje',
    month: 'Mês',
    week: 'Semana',
    day: 'Dia'
  },
  events: [],
  eventClick: handleEventClick,
  select: handleDateSelect
});

// Dialog for reservation details
const eventDialog = ref(false);
const selectedEvent = ref(null);

// Dialog for new reservation
const newReservationDialog = ref(false);
const newReservation = ref({
  title: '',
  description: '',
  start_time: null,
  end_time: null,
  room_id: null
});
const submitted = ref(false);

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
          description: 'Sala de aula padrão',
          capacity: 40, 
          department: 'Departamento Acadêmico',
          status: 'AVAILABLE'
        };
      } else if (roomId.value === '2') {
        room.value = { 
          id: 2, 
          name: 'Laboratório de Informática', 
          description: 'Laboratório com 30 computadores',
          capacity: 30, 
          department: 'Departamento de TI',
          status: 'OCCUPIED'
        };
      } else if (roomId.value === '3') {
        room.value = { 
          id: 3, 
          name: 'Auditório', 
          description: 'Auditório principal',
          capacity: 120, 
          department: 'Departamento Administrativo',
          status: 'AVAILABLE'
        };
      } else if (roomId.value === '4') {
        room.value = { 
          id: 4, 
          name: 'Sala de Reuniões', 
          description: 'Sala para reuniões e videoconferências',
          capacity: 15, 
          department: 'Departamento Administrativo',
          status: 'AVAILABLE'
        };
      } else if (roomId.value === '5') {
        room.value = { 
          id: 5, 
          name: 'Sala 102', 
          description: 'Sala de aula padrão',
          capacity: 40, 
          department: 'Departamento Acadêmico',
          status: 'MAINTENANCE'
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
      fetchReservations();
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

// Fetch reservations for this room
const fetchReservations = async () => {
  try {
    // Implement API call to get reservations for this room
    // const response = await api.getRoomReservations(roomId.value);
    // const events = response.map(reservation => ({
    //   id: reservation.id,
    //   title: reservation.title,
    //   start: reservation.start_time,
    //   end: reservation.end_time,
    //   extendedProps: {
    //     description: reservation.description,
    //     user: reservation.user,
    //     status: reservation.status
    //   },
    //   backgroundColor: getStatusColor(reservation.status)
    // }));
    // calendarOptions.value.events = events;
    
    // Mock data for now
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    const day = today.getDate();
    
    let events = [];
    
    if (roomId.value === '1') {
      events = [
        {
          id: 101,
          title: 'Aula de Matemática',
          start: new Date(year, month, day, 8, 0),
          end: new Date(year, month, day, 10, 0),
          extendedProps: {
            description: 'Aula de Cálculo I para turma de Engenharia',
            user: 'Prof. Carlos Silva',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E' // green for confirmed
        },
        {
          id: 102,
          title: 'Aula de Física',
          start: new Date(year, month, day, 14, 0),
          end: new Date(year, month, day, 16, 0),
          extendedProps: {
            description: 'Aula de Física Mecânica para turma de Engenharia',
            user: 'Prof. Ana Oliveira',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E'
        },
        {
          id: 103,
          title: 'Monitoria de Matemática',
          start: new Date(year, month, day + 1, 10, 0),
          end: new Date(year, month, day + 1, 12, 0),
          extendedProps: {
            description: 'Monitoria para alunos com dificuldade em Cálculo',
            user: 'Monitor Pedro Santos',
            status: 'PENDING'
          },
          backgroundColor: '#F59E0B' // amber for pending
        }
      ];
    } else if (roomId.value === '2') {
      events = [
        {
          id: 201,
          title: 'Aula de Programação',
          start: new Date(year, month, day - 1, 10, 0),
          end: new Date(year, month, day - 1, 12, 0),
          extendedProps: {
            description: 'Aula de Programação Web para turma de Sistemas de Informação',
            user: 'Prof. João Pereira',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E'
        },
        {
          id: 202,
          title: 'Curso de Web Design',
          start: new Date(year, month, day, 8, 0),
          end: new Date(year, month, day, 12, 0),
          extendedProps: {
            description: 'Curso intensivo de Web Design para alunos de Design',
            user: 'Prof. Mariana Costa',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E'
        },
        {
          id: 203,
          title: 'Laboratório de Redes',
          start: new Date(year, month, day + 2, 14, 0),
          end: new Date(year, month, day + 2, 18, 0),
          extendedProps: {
            description: 'Aula prática de configuração de redes',
            user: 'Prof. Ricardo Almeida',
            status: 'PENDING'
          },
          backgroundColor: '#F59E0B'
        },
        {
          id: 204,
          title: 'Manutenção de Equipamentos',
          start: new Date(year, month, day + 3, 8, 0),
          end: new Date(year, month, day + 3, 10, 0),
          extendedProps: {
            description: 'Manutenção preventiva dos computadores',
            user: 'Equipe de TI',
            status: 'CANCELLED'
          },
          backgroundColor: '#EF4444' // red for cancelled
        }
      ];
    } else if (roomId.value === '3') {
      events = [
        {
          id: 301,
          title: 'Palestra: Inteligência Artificial',
          start: new Date(year, month, day + 1, 14, 0),
          end: new Date(year, month, day + 1, 17, 0),
          extendedProps: {
            description: 'Palestra sobre avanços em IA e suas aplicações',
            user: 'Dr. Roberto Mendes',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E'
        },
        {
          id: 302,
          title: 'Formatura Turma 2023',
          start: new Date(year, month, day + 5, 18, 0),
          end: new Date(year, month, day + 5, 22, 0),
          extendedProps: {
            description: 'Cerimônia de formatura dos concluintes de 2023',
            user: 'Coordenação Acadêmica',
            status: 'CONFIRMED'
          },
          backgroundColor: '#22C55E'
        }
      ];
    } else {
      events = [];
    }
    
    calendarOptions.value = {
      ...calendarOptions.value,
      events
    };
  } catch (error) {
    console.error('Error fetching reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as reservas',
      life: 3000
    });
  }
};

// Handle event click
function handleEventClick(info) {
  selectedEvent.value = {
    id: info.event.id,
    title: info.event.title,
    start: info.event.start,
    end: info.event.end,
    description: info.event.extendedProps.description,
    user: info.event.extendedProps.user,
    status: info.event.extendedProps.status
  };
  eventDialog.value = true;
}

// Handle date select
function handleDateSelect(info) {
  if (!auth.isAuthenticated) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Você precisa estar logado para criar reservas',
      life: 3000
    });
    return;
  }
  
  newReservation.value = {
    title: '',
    description: '',
    start_time: info.start,
    end_time: info.end,
    room_id: roomId.value
  };
  
  newReservationDialog.value = true;
}

// Format date
const formatDate = (date) => {
  if (!date) return '';
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
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

// Save new reservation
const saveReservation = async () => {
  submitted.value = true;
  
  if (newReservation.value.title.trim() && newReservation.value.start_time && newReservation.value.end_time) {
    try {
      // Implement API call to create reservation
      // await api.createReservation(newReservation.value);
      
      // Mock success
      toast.add({
        severity: 'success',
        summary: 'Sucesso',
        detail: 'Reserva criada com sucesso',
        life: 3000
      });
      
      // Close dialog and refresh calendar
      newReservationDialog.value = false;
      submitted.value = false;
      
      // Add to calendar (in a real app, we would refetch from API)
      const newEvent = {
        id: Math.floor(Math.random() * 1000),
        title: newReservation.value.title,
        start: newReservation.value.start_time,
        end: newReservation.value.end_time,
        extendedProps: {
          description: newReservation.value.description,
          user: auth.user?.name || 'Usuário',
          status: 'PENDING'
        },
        backgroundColor: '#F59E0B' // amber for pending
      };
      
      calendarOptions.value = {
        ...calendarOptions.value,
        events: [...calendarOptions.value.events, newEvent]
      };
      
    } catch (error) {
      console.error('Error creating reservation:', error);
      toast.add({
        severity: 'error',
        summary: 'Erro',
        detail: 'Não foi possível criar a reserva',
        life: 3000
      });
    }
  }
};

// View reservation details
const viewReservation = (id) => {
  router.push(`/reservations/${id}`);
};

// Navigate to room details
const viewRoomDetails = () => {
  router.push(`/rooms/${roomId.value}`);
};

// Initialize component
onMounted(async () => {
  await fetchRoom();
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
        <div class="col-12">
          <div class="card">
            <div class="flex justify-content-between align-items-center mb-4">
              <div>
                <h2 class="m-0">Calendário: {{ room.name }}</h2>
                <p class="text-color-secondary mt-1 mb-0">Visualize e gerencie as reservas desta sala</p>
              </div>
              <div>
                <Button icon="pi pi-arrow-left" label="Voltar para Detalhes" class="p-button-outlined mr-2" @click="viewRoomDetails" />
                <Button icon="pi pi-plus" label="Nova Reserva" class="p-button-success" @click="newReservationDialog = true" v-if="auth.isAuthenticated" />
              </div>
            </div>
            
            <div class="calendar-container">
              <FullCalendar :options="calendarOptions" />
            </div>
            
            <div class="mt-4">
              <h4>Legenda</h4>
              <div class="flex flex-wrap gap-3">
                <div class="flex align-items-center">
                  <div class="color-box" style="background-color: #22C55E;"></div>
                  <span>Confirmada</span>
                </div>
                <div class="flex align-items-center">
                  <div class="color-box" style="background-color: #F59E0B;"></div>
                  <span>Pendente</span>
                </div>
                <div class="flex align-items-center">
                  <div class="color-box" style="background-color: #EF4444;"></div>
                  <span>Cancelada</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Event Details Dialog -->
      <Dialog v-model:visible="eventDialog" :style="{width: '450px'}" header="Detalhes da Reserva" :modal="true" class="p-fluid">
        <div v-if="selectedEvent">
          <div class="field">
            <h4>{{ selectedEvent.title }}</h4>
          </div>
          
          <div class="field">
            <label class="font-bold">Descrição</label>
            <p>{{ selectedEvent.description || 'Sem descrição' }}</p>
          </div>
          
          <div class="field">
            <label class="font-bold">Início</label>
            <p>{{ formatDate(selectedEvent.start) }}</p>
          </div>
          
          <div class="field">
            <label class="font-bold">Término</label>
            <p>{{ formatDate(selectedEvent.end) }}</p>
          </div>
          
          <div class="field">
            <label class="font-bold">Responsável</label>
            <p>{{ selectedEvent.user }}</p>
          </div>
          
          <div class="field">
            <label class="font-bold">Status</label>
            <Tag :value="getStatusLabel(selectedEvent.status)" :severity="getStatusSeverity(selectedEvent.status)" />
          </div>
        </div>
        
        <template #footer>
          <Button label="Fechar" icon="pi pi-times" class="p-button-text" @click="eventDialog = false" />
          <Button label="Ver Detalhes" icon="pi pi-eye" @click="viewReservation(selectedEvent?.id); eventDialog = false" />
        </template>
      </Dialog>
      
      <!-- New Reservation Dialog -->
      <Dialog v-model:visible="newReservationDialog" :style="{width: '450px'}" header="Nova Reserva" :modal="true" class="p-fluid">
        <div class="field">
          <label for="title">Título</label>
          <InputText id="title" v-model="newReservation.title" required autofocus :class="{'p-invalid': submitted && !newReservation.title}" />
          <small class="p-error" v-if="submitted && !newReservation.title">Título é obrigatório.</small>
        </div>
        
        <div class="field">
          <label for="description">Descrição</label>
          <Textarea id="description" v-model="newReservation.description" rows="3" />
        </div>
        
        <div class="field">
          <label for="start">Início</label>
          <Calendar id="start" v-model="newReservation.start_time" showTime hourFormat="24" :class="{'p-invalid': submitted && !newReservation.start_time}" />
          <small class="p-error" v-if="submitted && !newReservation.start_time">Data e hora de início são obrigatórias.</small>
        </div>
        
        <div class="field">
          <label for="end">Término</label>
          <Calendar id="end" v-model="newReservation.end_time" showTime hourFormat="24" :class="{'p-invalid': submitted && !newReservation.end_time}" />
          <small class="p-error" v-if="submitted && !newReservation.end_time">Data e hora de término são obrigatórias.</small>
        </div>
        
        <template #footer>
          <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="newReservationDialog = false" />
          <Button label="Salvar" icon="pi pi-check" @click="saveReservation" />
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

.calendar-container {
  height: 650px;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  margin-right: 8px;
}

h4 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-color-secondary);
  font-weight: 600;
}

:deep(.fc-event) {
  cursor: pointer;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem !important;
}

:deep(.fc-header-toolbar) {
  margin-bottom: 1.5rem !important;
}

@media screen and (max-width: 768px) {
  :deep(.fc-header-toolbar) {
    flex-direction: column;
    gap: 1rem;
  }
  
  :deep(.fc-toolbar-title) {
    font-size: 1.2rem !important;
  }
}
</style>
