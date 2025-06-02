<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const toast = useToast();

// Loading states
const loading = ref({
  stats: false,
  reservations: false,
  rooms: false
});

// Dashboard data
const stats = ref({
  totalReservations: 0,
  pendingReservations: 0,
  availableRooms: 0,
  totalRooms: 0
});

const recentReservations = ref([]);
const popularRooms = ref([]);

// Chart data
const reservationChartData = ref({
  labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho'],
  datasets: [
    {
      label: 'Reservas',
      data: [65, 59, 80, 81, 56, 55, 40],
      fill: false,
      borderColor: '#2196F3',
      tension: 0.4
    }
  ]
});

const roomUsageChartData = ref({
  labels: ['Sala 101', 'Sala 102', 'Laboratório 1', 'Auditório', 'Sala de Reuniões'],
  datasets: [
    {
      data: [30, 25, 22, 15, 8],
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    }
  ]
});

// Chart options
const chartOptions = ref({
  plugins: {
    legend: {
      position: 'bottom'
    }
  },
  responsive: true,
  maintainAspectRatio: false
});

// Computed properties
const userName = computed(() => {
  return auth.user?.name || 'Usuário';
});

const isAdmin = computed(() => {
  return auth.hasAdminAccess;
});

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    loading.value.stats = true;
    // Implement API call to get dashboard stats
    // const response = await api.getDashboardStats();
    // stats.value = response;
    
    // Mock data for now
    stats.value = {
      totalReservations: 245,
      pendingReservations: 12,
      availableRooms: 18,
      totalRooms: 25
    };
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as estatísticas do dashboard',
      life: 3000
    });
  } finally {
    loading.value.stats = false;
  }
};

// Fetch recent reservations
const fetchRecentReservations = async () => {
  try {
    loading.value.reservations = true;
    // Implement API call to get recent reservations
    // const response = await api.getRecentReservations();
    // recentReservations.value = response;
    
    // Mock data for now
    recentReservations.value = [
      { id: 1, room: 'Sala 101', user: 'João Silva', date: '2025-06-02', time: '14:00 - 16:00', status: 'APPROVED' },
      { id: 2, room: 'Laboratório 1', user: 'Maria Santos', date: '2025-06-03', time: '09:00 - 11:00', status: 'PENDING' },
      { id: 3, room: 'Auditório', user: 'Carlos Oliveira', date: '2025-06-04', time: '13:00 - 15:00', status: 'APPROVED' },
      { id: 4, room: 'Sala de Reuniões', user: 'Ana Pereira', date: '2025-06-05', time: '10:00 - 12:00', status: 'REJECTED' },
      { id: 5, room: 'Sala 102', user: 'Pedro Costa', date: '2025-06-06', time: '15:00 - 17:00', status: 'APPROVED' }
    ];
  } catch (error) {
    console.error('Error fetching recent reservations:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as reservas recentes',
      life: 3000
    });
  } finally {
    loading.value.reservations = false;
  }
};

// Fetch popular rooms
const fetchPopularRooms = async () => {
  try {
    loading.value.rooms = true;
    // Implement API call to get popular rooms
    // const response = await api.getPopularRooms();
    // popularRooms.value = response;
    
    // Mock data for now
    popularRooms.value = [
      { id: 1, name: 'Auditório', reservations: 45, availability: '75%' },
      { id: 2, name: 'Laboratório 1', reservations: 38, availability: '60%' },
      { id: 3, name: 'Sala 101', reservations: 32, availability: '80%' },
      { id: 4, name: 'Sala de Reuniões', reservations: 28, availability: '65%' },
      { id: 5, name: 'Sala 102', reservations: 25, availability: '85%' }
    ];
  } catch (error) {
    console.error('Error fetching popular rooms:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as salas populares',
      life: 3000
    });
  } finally {
    loading.value.rooms = false;
  }
};

// Get status severity
const getStatusSeverity = (status) => {
  switch (status) {
    case 'APPROVED':
      return 'success';
    case 'PENDING':
      return 'warning';
    case 'REJECTED':
      return 'danger';
    default:
      return 'info';
  }
};

// Format date
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

// Navigate to reservation details
const viewReservation = (id) => {
  // Navigate to reservation details
  // router.push(`/reservations/${id}`);
};

// Navigate to room details
const viewRoom = (id) => {
  // Navigate to room details
  // router.push(`/rooms/${id}`);
};

// Fetch all data on component mount
onMounted(async () => {
  await Promise.all([
    fetchDashboardData(),
    fetchRecentReservations(),
    fetchPopularRooms()
  ]);
});
</script>

<template>
  <div>
    <!-- Welcome section -->
    <div class="grid">
      <div class="col-12">
        <div class="card mb-0">
          <div class="flex justify-content-between flex-wrap">
            <div class="flex align-items-center justify-content-center">
              <i class="pi pi-user mr-2 text-2xl"></i>
              <div class="text-900 font-medium text-xl">Bem-vindo(a), {{ userName }}!</div>
            </div>
            <div>
              <Button icon="pi pi-refresh" label="Atualizar" @click="fetchDashboardData" class="p-button-outlined mr-2" />
              <Button icon="pi pi-plus" label="Nova Reserva" class="p-button-primary" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats widgets -->
    <div class="grid mt-3">
      <div class="col-12 md:col-6 lg:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Reservas Totais</span>
              <div class="text-900 font-medium text-xl">{{ stats.totalReservations }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-calendar text-blue-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">{{ stats.pendingReservations }} pendentes </span>
          <span class="text-500">desde o último mês</span>
          <ProgressBar :value="(stats.pendingReservations / stats.totalReservations) * 100" class="mt-3" style="height: 6px" />
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Salas Disponíveis</span>
              <div class="text-900 font-medium text-xl">{{ stats.availableRooms }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-map-marker text-orange-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">{{ stats.availableRooms }} disponíveis </span>
          <span class="text-500">de {{ stats.totalRooms }} salas</span>
          <ProgressBar :value="(stats.availableRooms / stats.totalRooms) * 100" class="mt-3" style="height: 6px" />
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Minhas Reservas</span>
              <div class="text-900 font-medium text-xl">12</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-bookmark text-cyan-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">2 pendentes </span>
          <span class="text-500">para aprovação</span>
          <ProgressBar value="25" class="mt-3" style="height: 6px" />
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Taxa de Ocupação</span>
              <div class="text-900 font-medium text-xl">68%</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-purple-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-percentage text-purple-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">+12% </span>
          <span class="text-500">desde o último mês</span>
          <ProgressBar value="68" class="mt-3" style="height: 6px" />
        </div>
      </div>
    </div>

    <!-- Charts section -->
    <div class="grid">
      <!-- Reservation trend chart -->
      <div class="col-12 lg:col-6">
        <div class="card">
          <h5>Tendência de Reservas</h5>
          <Chart type="line" :data="reservationChartData" :options="chartOptions" class="h-20rem" />
        </div>
      </div>
      
      <!-- Room usage chart -->
      <div class="col-12 lg:col-6">
        <div class="card">
          <h5>Uso de Salas</h5>
          <Chart type="pie" :data="roomUsageChartData" :options="chartOptions" class="h-20rem" />
        </div>
      </div>
    </div>

    <!-- Recent reservations and popular rooms -->
    <div class="grid">
      <!-- Recent reservations -->
      <div class="col-12 lg:col-8">
        <div class="card">
          <h5>Reservas Recentes</h5>
          <DataTable 
            :value="recentReservations" 
            :paginator="true" 
            :rows="5"
            :loading="loading.reservations"
            responsiveLayout="scroll"
            stripedRows
            class="p-datatable-sm"
          >
            <Column field="room" header="Sala"></Column>
            <Column field="date" header="Data">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            <Column field="time" header="Horário"></Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Ações">
              <template #body="{ data }">
                <Button icon="pi pi-eye" class="p-button-rounded p-button-text" @click="viewReservation(data.id)" />
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      
      <!-- Popular rooms -->
      <div class="col-12 lg:col-4">
        <div class="card">
          <h5>Salas Mais Populares</h5>
          <DataTable 
            :value="popularRooms" 
            :loading="loading.rooms"
            responsiveLayout="scroll"
            class="p-datatable-sm"
          >
            <Column field="name" header="Sala"></Column>
            <Column field="reservations" header="Reservas"></Column>
            <Column field="availability" header="Disponibilidade"></Column>
            <Column header="Ações">
              <template #body="{ data }">
                <Button icon="pi pi-eye" class="p-button-rounded p-button-text" @click="viewRoom(data.id)" />
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </div>

    <!-- Admin section -->
    <div v-if="isAdmin" class="grid">
      <div class="col-12">
        <div class="card">
          <h5>Painel Administrativo</h5>
          <div class="grid">
            <div class="col-12 md:col-4">
              <div class="p-3 border-1 surface-border border-round">
                <div class="flex align-items-center mb-3">
                  <i class="pi pi-users text-xl text-primary mr-2"></i>
                  <span class="text-900 font-medium">Gerenciar Usuários</span>
                </div>
                <p class="text-600 mt-0 mb-3 line-height-3">Adicione, edite ou remova usuários do sistema.</p>
                <Button label="Acessar" icon="pi pi-arrow-right" class="p-button-outlined w-full" />
              </div>
            </div>
            
            <div class="col-12 md:col-4">
              <div class="p-3 border-1 surface-border border-round">
                <div class="flex align-items-center mb-3">
                  <i class="pi pi-building text-xl text-primary mr-2"></i>
                  <span class="text-900 font-medium">Gerenciar Departamentos</span>
                </div>
                <p class="text-600 mt-0 mb-3 line-height-3">Organize os departamentos da instituição.</p>
                <Button label="Acessar" icon="pi pi-arrow-right" class="p-button-outlined w-full" />
              </div>
            </div>
            
            <div class="col-12 md:col-4">
              <div class="p-3 border-1 surface-border border-round">
                <div class="flex align-items-center mb-3">
                  <i class="pi pi-chart-bar text-xl text-primary mr-2"></i>
                  <span class="text-900 font-medium">Relatórios</span>
                </div>
                <p class="text-600 mt-0 mb-3 line-height-3">Visualize e exporte relatórios detalhados.</p>
                <Button label="Acessar" icon="pi pi-arrow-right" class="p-button-outlined w-full" />
              </div>
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

.p-datatable .p-datatable-thead > tr > th {
  background: var(--surface-ground);
  color: var(--text-color);
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.p-datatable .p-datatable-tbody > tr > td {
  padding: 0.75rem 1rem;
}

.h-20rem {
  height: 20rem;
}
</style>
