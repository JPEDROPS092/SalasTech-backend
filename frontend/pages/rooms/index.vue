<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Data
const rooms = ref([]);
const selectedRooms = ref([]);
const loading = ref(false);
const totalRecords = ref(0);

// Filters
const filters = reactive({
  global: { value: null, matchMode: 'contains' },
  name: { value: null, matchMode: 'contains' },
  capacity: { value: null, matchMode: 'gte' },
  department: { value: null, matchMode: 'contains' },
  status: { value: null, matchMode: 'equals' }
});

// Pagination
const lazyParams = ref({
  first: 0,
  rows: 10,
  page: 1,
  sortField: 'name',
  sortOrder: 1
});

// Departments for filter
const departments = ref([]);

// Status options
const statusOptions = ref([
  { label: 'Disponível', value: 'AVAILABLE' },
  { label: 'Ocupada', value: 'OCCUPIED' },
  { label: 'Em Manutenção', value: 'MAINTENANCE' }
]);

// Dialog visibility
const deleteRoomDialog = ref(false);
const deleteRoomsDialog = ref(false);
const roomDialog = ref(false);

// Selected room for operations
const room = ref({
  id: null,
  name: '',
  description: '',
  capacity: 0,
  department_id: null,
  resources: [],
  status: 'AVAILABLE'
});

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

// Validation
const submitted = ref(false);

// Fetch rooms data
const loadRooms = async () => {
  try {
    loading.value = true;
    
    // Implement API call to get rooms with pagination
    // const response = await api.getRooms(lazyParams.value);
    // rooms.value = response.data;
    // totalRecords.value = response.total;
    
    // Mock data for now
    setTimeout(() => {
      rooms.value = [
        { 
          id: 1, 
          name: 'Sala 101', 
          description: 'Sala de aula padrão', 
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'AVAILABLE'
        },
        { 
          id: 2, 
          name: 'Laboratório de Informática', 
          description: 'Laboratório com 30 computadores', 
          capacity: 30, 
          department: 'Departamento de TI',
          department_id: 1,
          resources: [1, 2, 3, 4],
          status: 'OCCUPIED'
        },
        { 
          id: 3, 
          name: 'Auditório', 
          description: 'Auditório principal', 
          capacity: 120, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 3, 4, 5],
          status: 'AVAILABLE'
        },
        { 
          id: 4, 
          name: 'Sala de Reuniões', 
          description: 'Sala para reuniões e videoconferências', 
          capacity: 15, 
          department: 'Departamento Administrativo',
          department_id: 3,
          resources: [1, 2, 3, 4, 7],
          status: 'AVAILABLE'
        },
        { 
          id: 5, 
          name: 'Sala 102', 
          description: 'Sala de aula padrão', 
          capacity: 40, 
          department: 'Departamento Acadêmico',
          department_id: 2,
          resources: [1, 3, 6],
          status: 'MAINTENANCE'
        }
      ];
      totalRecords.value = 5;
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('Error loading rooms:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar as salas',
      life: 3000
    });
    loading.value = false;
  }
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

// Handle page change
const onPage = (event) => {
  lazyParams.value.first = event.first;
  lazyParams.value.rows = event.rows;
  lazyParams.value.page = event.page + 1;
  loadRooms();
};

// Handle sort
const onSort = (event) => {
  lazyParams.value.sortField = event.sortField;
  lazyParams.value.sortOrder = event.sortOrder;
  loadRooms();
};

// Handle filter
const onFilter = () => {
  lazyParams.value.first = 0;
  lazyParams.value.page = 1;
  loadRooms();
};

// Open new room dialog
const openNew = () => {
  room.value = {
    id: null,
    name: '',
    description: '',
    capacity: 0,
    department_id: null,
    resources: [],
    status: 'AVAILABLE'
  };
  submitted.value = false;
  roomDialog.value = true;
};

// Hide dialog
const hideDialog = () => {
  roomDialog.value = false;
  submitted.value = false;
};

// Save room
const saveRoom = () => {
  submitted.value = true;

  if (room.value.name.trim() && room.value.capacity > 0) {
    try {
      if (room.value.id) {
        // Update existing room
        // await api.updateRoom(room.value.id, room.value);
        
        // Update local data
        const index = rooms.value.findIndex(r => r.id === room.value.id);
        if (index !== -1) {
          // Find department name
          const dept = departments.value.find(d => d.id === room.value.department_id);
          room.value.department = dept ? dept.name : '';
          
          rooms.value[index] = { ...room.value };
        }
        
        toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Sala atualizada',
          life: 3000
        });
      } else {
        // Create new room
        // const response = await api.createRoom(room.value);
        // room.value.id = response.id;
        
        // Mock new ID
        room.value.id = rooms.value.length + 1;
        
        // Find department name
        const dept = departments.value.find(d => d.id === room.value.department_id);
        room.value.department = dept ? dept.name : '';
        
        // Add to local data
        rooms.value.push({ ...room.value });
        
        toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Sala criada',
          life: 3000
        });
      }
      
      roomDialog.value = false;
      room.value = {};
    } catch (error) {
      console.error('Error saving room:', error);
      toast.add({
        severity: 'error',
        summary: 'Erro',
        detail: 'Não foi possível salvar a sala',
        life: 3000
      });
    }
  }
};

// Edit room
const editRoom = (editRoom) => {
  room.value = { ...editRoom };
  roomDialog.value = true;
};

// Confirm delete room
const confirmDeleteRoom = (editRoom) => {
  room.value = editRoom;
  deleteRoomDialog.value = true;
};

// Delete room
const deleteRoom = async () => {
  try {
    // Implement API call to delete room
    // await api.deleteRoom(room.value.id);
    
    // Update local data
    rooms.value = rooms.value.filter(r => r.id !== room.value.id);
    
    deleteRoomDialog.value = false;
    room.value = {};
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Sala excluída',
      life: 3000
    });
  } catch (error) {
    console.error('Error deleting room:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível excluir a sala',
      life: 3000
    });
  }
};

// Confirm delete selected rooms
const confirmDeleteSelected = () => {
  deleteRoomsDialog.value = true;
};

// Delete selected rooms
const deleteSelectedRooms = async () => {
  try {
    // Implement API call to delete multiple rooms
    // await Promise.all(selectedRooms.value.map(room => api.deleteRoom(room.id)));
    
    // Update local data
    rooms.value = rooms.value.filter(r => !selectedRooms.value.includes(r));
    
    deleteRoomsDialog.value = false;
    selectedRooms.value = [];
    
    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Salas excluídas',
      life: 3000
    });
  } catch (error) {
    console.error('Error deleting rooms:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível excluir as salas',
      life: 3000
    });
  }
};

// View room details
const viewRoom = (id) => {
  router.push(`/rooms/${id}`);
};

// View room calendar
const viewRoomCalendar = (id) => {
  router.push(`/rooms/${id}/calendar`);
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
onMounted(async () => {
  await fetchDepartments();
  await loadRooms();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <Toast />
        <ConfirmDialog />
        
        <div class="flex justify-content-between align-items-center mb-4">
          <h5 class="m-0">Gerenciamento de Salas</h5>
          <div>
            <Button label="Nova Sala" icon="pi pi-plus" class="p-button-success mr-2" @click="openNew" v-if="auth.hasAdminAccess" />
            <Button label="Excluir" icon="pi pi-trash" class="p-button-danger" @click="confirmDeleteSelected" 
                   :disabled="!selectedRooms || !selectedRooms.length" v-if="auth.hasAdminAccess" />
          </div>
        </div>
        
        <DataTable 
          :value="rooms" 
          v-model:selection="selectedRooms" 
          dataKey="id"
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} salas"
          responsiveLayout="scroll"
          :loading="loading"
          :filters="filters"
          filterDisplay="menu"
          :globalFilterFields="['name', 'description', 'capacity', 'department']"
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
          
          <Column field="name" header="Nome" :sortable="true" style="min-width: 12rem">
            <template #filter="{ filterModel, filterCallback }">
              <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Buscar por nome" class="p-column-filter" />
            </template>
          </Column>
          
          <Column field="capacity" header="Capacidade" :sortable="true" style="min-width: 8rem">
            <template #filter="{ filterModel, filterCallback }">
              <InputNumber v-model="filterModel.value" @input="filterCallback()" placeholder="Mínimo" class="p-column-filter" />
            </template>
          </Column>
          
          <Column field="department" header="Departamento" :sortable="true" style="min-width: 12rem">
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown 
                v-model="filterModel.value" 
                @change="filterCallback()"
                :options="departments" 
                optionLabel="name" 
                placeholder="Selecione um departamento" 
                class="p-column-filter" 
                showClear
              />
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
          
          <Column field="resources" header="Recursos" style="min-width: 14rem">
            <template #body="{ data }">
              <div class="flex flex-wrap gap-1">
                <Chip v-for="id in data.resources" :key="id" :label="resourceOptions.find(r => r.id === id)?.name" class="mr-1 mb-1" />
              </div>
            </template>
          </Column>
          
          <Column header="Ações" style="min-width: 12rem">
            <template #body="{ data }">
              <div class="flex">
                <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-info mr-2" @click="viewRoom(data.id)" />
                <Button icon="pi pi-calendar" class="p-button-rounded p-button-text p-button-success mr-2" @click="viewRoomCalendar(data.id)" />
                <Button icon="pi pi-pencil" class="p-button-rounded p-button-text p-button-warning mr-2" @click="editRoom(data)" v-if="auth.hasAdminAccess" />
                <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="confirmDeleteRoom(data)" v-if="auth.hasAdminAccess" />
              </div>
            </template>
          </Column>
        </DataTable>
        
        <!-- Room Dialog -->
        <Dialog v-model:visible="roomDialog" :style="{width: '550px'}" header="Detalhes da Sala" :modal="true" class="p-fluid">
          <div class="field">
            <label for="name">Nome</label>
            <InputText id="name" v-model="room.name" required autofocus :class="{'p-invalid': submitted && !room.name}" />
            <small class="p-error" v-if="submitted && !room.name">Nome é obrigatório.</small>
          </div>
          
          <div class="field">
            <label for="description">Descrição</label>
            <Textarea id="description" v-model="room.description" rows="3" />
          </div>
          
          <div class="field">
            <label for="capacity">Capacidade</label>
            <InputNumber id="capacity" v-model="room.capacity" :min="1" required :class="{'p-invalid': submitted && !room.capacity}" />
            <small class="p-error" v-if="submitted && !room.capacity">Capacidade é obrigatória e deve ser maior que zero.</small>
          </div>
          
          <div class="field">
            <label for="department">Departamento</label>
            <Dropdown id="department" v-model="room.department_id" :options="departments" optionLabel="name" optionValue="id" placeholder="Selecione um departamento" />
          </div>
          
          <div class="field">
            <label for="resources">Recursos</label>
            <MultiSelect id="resources" v-model="room.resources" :options="resourceOptions" optionLabel="name" optionValue="id" placeholder="Selecione os recursos" display="chip" />
          </div>
          
          <div class="field">
            <label for="status">Status</label>
            <Dropdown id="status" v-model="room.status" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Selecione um status" />
          </div>
          
          <template #footer>
            <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
            <Button label="Salvar" icon="pi pi-check" class="p-button-text" @click="saveRoom" />
          </template>
        </Dialog>
        
        <!-- Delete Room Dialog -->
        <Dialog v-model:visible="deleteRoomDialog" :style="{width: '450px'}" header="Confirmar" :modal="true">
          <div class="confirmation-content">
            <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
            <span v-if="room">Tem certeza que deseja excluir <b>{{ room.name }}</b>?</span>
          </div>
          <template #footer>
            <Button label="Não" icon="pi pi-times" class="p-button-text" @click="deleteRoomDialog = false" />
            <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="deleteRoom" />
          </template>
        </Dialog>
        
        <!-- Delete Multiple Rooms Dialog -->
        <Dialog v-model:visible="deleteRoomsDialog" :style="{width: '450px'}" header="Confirmar" :modal="true">
          <div class="confirmation-content">
            <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
            <span v-if="selectedRooms && selectedRooms.length">Tem certeza que deseja excluir as salas selecionadas?</span>
          </div>
          <template #footer>
            <Button label="Não" icon="pi pi-times" class="p-button-text" @click="deleteRoomsDialog = false" />
            <Button label="Sim" icon="pi pi-check" class="p-button-text" @click="deleteSelectedRooms" />
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
