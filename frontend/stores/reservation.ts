import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { reservationsService, Reservation, ReservationWithDetails, PaginatedResponse } from '~/services/reservations';

export const useReservationStore = defineStore('reservation', () => {
  // Estado
  const reservations = ref<ReservationWithDetails[]>([]);
  const currentReservation = ref<ReservationWithDetails | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const totalRecords = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);
  
  // Getters
  const pendingReservations = computed(() => 
    reservations.value.filter(r => r.status === 'PENDING')
  );
  
  const confirmedReservations = computed(() => 
    reservations.value.filter(r => r.status === 'CONFIRMED')
  );
  
  const cancelledReservations = computed(() => 
    reservations.value.filter(r => r.status === 'CANCELLED')
  );
  
  const isLoading = computed(() => loading.value);
  
  // Ações
  
  /**
   * Carregar todas as reservas com paginação e filtros
   */
  async function fetchReservations(page = 1, limit = 10, sortField = 'start_time', sortOrder = -1, filters = {}) {
    try {
      loading.value = true;
      error.value = null;
      
      const params = {
        page,
        limit,
        sortField,
        sortOrder
      };
      
      const response = await reservationsService.getReservations(params, filters);
      
      reservations.value = response.data;
      totalRecords.value = response.total;
      currentPage.value = page;
      pageSize.value = limit;
      
      return response;
    } catch (err) {
      console.error('Error fetching reservations:', err);
      error.value = 'Não foi possível carregar as reservas';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Buscar uma reserva específica por ID
   */
  async function fetchReservation(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.getReservation(id);
      currentReservation.value = response;
      
      return response;
    } catch (err) {
      console.error(`Error fetching reservation ${id}:`, err);
      error.value = 'Não foi possível carregar os detalhes da reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Criar uma nova reserva
   */
  async function createReservation(reservation: Reservation) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.createReservation(reservation);
      
      // Adicionar a nova reserva ao estado se estiver na mesma página
      if (reservations.value.length > 0) {
        reservations.value = [...reservations.value, response];
      }
      
      currentReservation.value = response;
      
      return response;
    } catch (err) {
      console.error('Error creating reservation:', err);
      error.value = 'Não foi possível criar a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Atualizar uma reserva existente
   */
  async function updateReservation(id: string | number, data: Partial<Reservation>) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.updateReservation(id, data);
      
      // Atualizar a reserva no estado
      const index = reservations.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reservations.value[index] = response;
      }
      
      if (currentReservation.value && currentReservation.value.id === id) {
        currentReservation.value = response;
      }
      
      return response;
    } catch (err) {
      console.error(`Error updating reservation ${id}:`, err);
      error.value = 'Não foi possível atualizar a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Excluir uma reserva
   */
  async function deleteReservation(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      await reservationsService.deleteReservation(id);
      
      // Remover a reserva do estado
      reservations.value = reservations.value.filter(r => r.id !== id);
      
      if (currentReservation.value && currentReservation.value.id === id) {
        currentReservation.value = null;
      }
      
      return true;
    } catch (err) {
      console.error(`Error deleting reservation ${id}:`, err);
      error.value = 'Não foi possível excluir a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Carregar as reservas do usuário atual
   */
  async function fetchUserReservations(userId: string | number, page = 1, limit = 10, sortField = 'start_time', sortOrder = -1) {
    try {
      loading.value = true;
      error.value = null;
      
      const params = {
        page,
        limit,
        sortField,
        sortOrder
      };
      
      const response = await reservationsService.getUserReservations(userId, params);
      
      reservations.value = response.data;
      totalRecords.value = response.total;
      currentPage.value = page;
      pageSize.value = limit;
      
      return response;
    } catch (err) {
      console.error(`Error fetching user reservations for user ${userId}:`, err);
      error.value = 'Não foi possível carregar suas reservas';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Carregar reservas pendentes (para administradores)
   */
  async function fetchPendingReservations(page = 1, limit = 10, sortField = 'created_at', sortOrder = -1) {
    try {
      loading.value = true;
      error.value = null;
      
      const params = {
        page,
        limit,
        sortField,
        sortOrder
      };
      
      const response = await reservationsService.getPendingReservations(params);
      
      reservations.value = response.data;
      totalRecords.value = response.total;
      currentPage.value = page;
      pageSize.value = limit;
      
      return response;
    } catch (err) {
      console.error('Error fetching pending reservations:', err);
      error.value = 'Não foi possível carregar as reservas pendentes';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Aprovar uma reserva (para administradores)
   */
  async function approveReservation(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.approveReservation(id);
      
      // Atualizar a reserva no estado
      const index = reservations.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reservations.value[index] = response;
      }
      
      if (currentReservation.value && currentReservation.value.id === id) {
        currentReservation.value = response;
      }
      
      return response;
    } catch (err) {
      console.error(`Error approving reservation ${id}:`, err);
      error.value = 'Não foi possível aprovar a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Rejeitar uma reserva (para administradores)
   */
  async function rejectReservation(id: string | number, reason: string) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.rejectReservation(id, reason);
      
      // Atualizar a reserva no estado
      const index = reservations.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reservations.value[index] = response;
      }
      
      if (currentReservation.value && currentReservation.value.id === id) {
        currentReservation.value = response;
      }
      
      return response;
    } catch (err) {
      console.error(`Error rejecting reservation ${id}:`, err);
      error.value = 'Não foi possível rejeitar a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Verificar conflitos de reservas para uma sala
   */
  async function checkRoomConflicts(roomId: string | number, startTime: string, endTime: string, excludeReservationId?: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.checkRoomConflicts(roomId, startTime, endTime, excludeReservationId);
      
      return response;
    } catch (err) {
      console.error(`Error checking conflicts for room ${roomId}:`, err);
      error.value = 'Não foi possível verificar conflitos de horário';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Carregar reservas para uma sala específica
   */
  async function fetchRoomReservations(roomId: string | number, startDate?: string, endDate?: string) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.getRoomReservations(roomId, startDate, endDate);
      
      reservations.value = response;
      
      return response;
    } catch (err) {
      console.error(`Error fetching reservations for room ${roomId}:`, err);
      error.value = 'Não foi possível carregar as reservas da sala';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Cancelar uma reserva
   */
  async function cancelReservation(id: string | number) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await reservationsService.updateReservation(id, { status: 'CANCELLED' });
      
      // Atualizar a reserva no estado
      const index = reservations.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reservations.value[index] = response;
      }
      
      if (currentReservation.value && currentReservation.value.id === id) {
        currentReservation.value = response;
      }
      
      return response;
    } catch (err) {
      console.error(`Error cancelling reservation ${id}:`, err);
      error.value = 'Não foi possível cancelar a reserva';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Limpar o estado
   */
  function clearState() {
    reservations.value = [];
    currentReservation.value = null;
    error.value = null;
    totalRecords.value = 0;
    currentPage.value = 1;
  }
  
  return {
    // Estado
    reservations,
    currentReservation,
    loading,
    error,
    totalRecords,
    currentPage,
    pageSize,
    
    // Getters
    pendingReservations,
    confirmedReservations,
    cancelledReservations,
    isLoading,
    
    // Ações
    fetchReservations,
    fetchReservation,
    createReservation,
    updateReservation,
    deleteReservation,
    fetchUserReservations,
    fetchPendingReservations,
    approveReservation,
    rejectReservation,
    checkRoomConflicts,
    fetchRoomReservations,
    cancelReservation,
    clearState
  };
});
