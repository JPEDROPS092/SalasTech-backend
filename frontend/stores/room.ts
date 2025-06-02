import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { roomsService, Room, RoomWithDetails, Department, RoomResource, PaginatedResponse } from '~/services/rooms';

export const useRoomStore = defineStore('room', () => {
  // Estado
  const rooms = ref<RoomWithDetails[]>([]);
  const currentRoom = ref<RoomWithDetails | null>(null);
  const departments = ref<Department[]>([]);
  const resources = ref<RoomResource[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const totalRecords = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);
  
  // Getters
  const activeRooms = computed(() => 
    rooms.value.filter(r => r.status === 'ACTIVE')
  );
  
  const inactiveRooms = computed(() => 
    rooms.value.filter(r => r.status === 'INACTIVE' || r.status === 'MAINTENANCE')
  );
  
  const isLoading = computed(() => loading.value);
  
  // Ações
  
  /**
   * Carregar todas as salas com paginação e filtros
   */
  async function fetchRooms(page = 1, limit = 10, sortField = 'name', sortOrder = 1, filters = {}) {
    try {
      loading.value = true;
      error.value = null;
      
      const params = {
        page,
        limit,
        sortField,
        sortOrder
      };
      
      const response = await roomsService.getRooms(params, filters);
      
      rooms.value = response.data;
      totalRecords.value = response.total;
      currentPage.value = page;
      pageSize.value = limit;
      
      return response;
    } catch (err) {
      console.error('Error fetching rooms:', err);
      error.value = 'Não foi possível carregar as salas';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Buscar uma sala específica por ID
   */
  async function fetchRoom(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.getRoom(id);
      currentRoom.value = response;
      
      return response;
    } catch (err) {
      console.error(`Error fetching room ${id}:`, err);
      error.value = 'Não foi possível carregar os detalhes da sala';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Criar uma nova sala
   */
  async function createRoom(room: Room, resourceIds?: number[]) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.createRoom(room, resourceIds);
      
      // Adicionar a nova sala ao estado se estiver na mesma página
      if (rooms.value.length > 0) {
        rooms.value = [...rooms.value, response];
      }
      
      currentRoom.value = response;
      
      return response;
    } catch (err) {
      console.error('Error creating room:', err);
      error.value = 'Não foi possível criar a sala';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Atualizar uma sala existente
   */
  async function updateRoom(id: string | number, data: Partial<Room>, resourceIds?: number[]) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.updateRoom(id, data, resourceIds);
      
      // Atualizar a sala no estado
      const index = rooms.value.findIndex(r => r.id === id);
      if (index !== -1) {
        rooms.value[index] = response;
      }
      
      if (currentRoom.value && currentRoom.value.id === id) {
        currentRoom.value = response;
      }
      
      return response;
    } catch (err) {
      console.error(`Error updating room ${id}:`, err);
      error.value = 'Não foi possível atualizar a sala';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Excluir uma sala
   */
  async function deleteRoom(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      await roomsService.deleteRoom(id);
      
      // Remover a sala do estado
      rooms.value = rooms.value.filter(r => r.id !== id);
      
      if (currentRoom.value && currentRoom.value.id === id) {
        currentRoom.value = null;
      }
      
      return true;
    } catch (err) {
      console.error(`Error deleting room ${id}:`, err);
      error.value = 'Não foi possível excluir a sala';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Carregar todos os departamentos
   */
  async function fetchDepartments() {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.getDepartments();
      departments.value = response;
      
      return response;
    } catch (err) {
      console.error('Error fetching departments:', err);
      error.value = 'Não foi possível carregar os departamentos';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Carregar todos os recursos disponíveis para salas
   */
  async function fetchRoomResources() {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.getRoomResources();
      resources.value = response;
      
      return response;
    } catch (err) {
      console.error('Error fetching room resources:', err);
      error.value = 'Não foi possível carregar os recursos';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Buscar salas disponíveis com base em critérios
   */
  async function findAvailableRooms(startTime: string, endTime: string, capacity?: number, departmentId?: number, resourceIds?: number[]) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await roomsService.findAvailableRooms(startTime, endTime, capacity, departmentId, resourceIds);
      
      return response;
    } catch (err) {
      console.error('Error finding available rooms:', err);
      error.value = 'Não foi possível encontrar salas disponíveis';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Limpar o estado
   */
  function clearState() {
    rooms.value = [];
    currentRoom.value = null;
    error.value = null;
    totalRecords.value = 0;
    currentPage.value = 1;
  }
  
  return {
    // Estado
    rooms,
    currentRoom,
    departments,
    resources,
    loading,
    error,
    totalRecords,
    currentPage,
    pageSize,
    
    // Getters
    activeRooms,
    inactiveRooms,
    isLoading,
    
    // Ações
    fetchRooms,
    fetchRoom,
    createRoom,
    updateRoom,
    deleteRoom,
    fetchDepartments,
    fetchRoomResources,
    findAvailableRooms,
    clearState
  };
});
