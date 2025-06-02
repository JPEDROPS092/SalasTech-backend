import { useCookie } from 'nuxt/app';

// Tipos
export interface Reservation {
  id?: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  room_id: number;
  user_id?: number;
  status: 'PENDING' | 'CONFIRMED' | 'CANCELLED';
  rejection_reason?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ReservationWithDetails extends Reservation {
  room?: {
    id: number;
    name: string;
    capacity: number;
    department: string;
    location: string;
  };
  user?: {
    id: number;
    name: string;
    email: string;
    role: string;
  };
}

export interface ReservationFilters {
  start_date?: string;
  end_date?: string;
  room_id?: number;
  status?: string;
  user_id?: number;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortField?: string;
  sortOrder?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

class ReservationsService {
  private baseURL: string;
  private headers: Record<string, string>;

  constructor() {
    this.baseURL = process.env.NODE_ENV === 'production' 
      ? '/api' 
      : 'http://localhost:8000/api';
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  private getAuthHeader(): Record<string, string> {
    const token = useCookie('auth_token').value;
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  /**
   * Obter todas as reservas com paginação e filtros
   */
  async getReservations(
    params: PaginationParams,
    filters?: ReservationFilters
  ): Promise<PaginatedResponse<ReservationWithDetails>> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      
      // Paginação
      queryParams.append('page', params.page.toString());
      queryParams.append('limit', params.limit.toString());
      
      // Ordenação
      if (params.sortField) {
        queryParams.append('sort_by', params.sortField);
        queryParams.append('sort_order', params.sortOrder?.toString() || '1');
      }
      
      // Filtros
      if (filters) {
        if (filters.start_date) queryParams.append('start_date', filters.start_date);
        if (filters.end_date) queryParams.append('end_date', filters.end_date);
        if (filters.room_id) queryParams.append('room_id', filters.room_id.toString());
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.user_id) queryParams.append('user_id', filters.user_id.toString());
      }
      
      const response = await $fetch<PaginatedResponse<ReservationWithDetails>>(
        `${this.baseURL}/reservations?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching reservations:', error);
      throw error;
    }
  }

  /**
   * Obter uma reserva específica por ID
   */
  async getReservation(id: string | number): Promise<ReservationWithDetails> {
    try {
      const response = await $fetch<ReservationWithDetails>(
        `${this.baseURL}/reservations/${id}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error fetching reservation with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Criar uma nova reserva
   */
  async createReservation(reservation: Reservation): Promise<ReservationWithDetails> {
    try {
      const response = await $fetch<ReservationWithDetails>(
        `${this.baseURL}/reservations`,
        {
          method: 'POST',
          body: reservation,
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error creating reservation:', error);
      throw error;
    }
  }

  /**
   * Atualizar uma reserva existente
   */
  async updateReservation(
    id: string | number, 
    reservation: Partial<Reservation>
  ): Promise<ReservationWithDetails> {
    try {
      const response = await $fetch<ReservationWithDetails>(
        `${this.baseURL}/reservations/${id}`,
        {
          method: 'PUT',
          body: reservation,
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error updating reservation with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Excluir uma reserva
   */
  async deleteReservation(id: string | number): Promise<void> {
    try {
      await $fetch(
        `${this.baseURL}/reservations/${id}`,
        {
          method: 'DELETE',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
    } catch (error) {
      console.error(`Error deleting reservation with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Obter reservas do usuário atual
   */
  async getUserReservations(
    userId: string | number,
    params: PaginationParams
  ): Promise<PaginatedResponse<ReservationWithDetails>> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      
      // Paginação
      queryParams.append('page', params.page.toString());
      queryParams.append('limit', params.limit.toString());
      
      // Ordenação
      if (params.sortField) {
        queryParams.append('sort_by', params.sortField);
        queryParams.append('sort_order', params.sortOrder?.toString() || '1');
      }
      
      const response = await $fetch<PaginatedResponse<ReservationWithDetails>>(
        `${this.baseURL}/users/${userId}/reservations?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error fetching reservations for user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Obter reservas pendentes (para administradores)
   */
  async getPendingReservations(
    params: PaginationParams
  ): Promise<PaginatedResponse<ReservationWithDetails>> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      
      // Paginação
      queryParams.append('page', params.page.toString());
      queryParams.append('limit', params.limit.toString());
      queryParams.append('status', 'PENDING');
      
      // Ordenação
      if (params.sortField) {
        queryParams.append('sort_by', params.sortField);
        queryParams.append('sort_order', params.sortOrder?.toString() || '1');
      }
      
      const response = await $fetch<PaginatedResponse<ReservationWithDetails>>(
        `${this.baseURL}/reservations?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching pending reservations:', error);
      throw error;
    }
  }

  /**
   * Aprovar uma reserva (para administradores)
   */
  async approveReservation(id: string | number): Promise<ReservationWithDetails> {
    try {
      const response = await $fetch<ReservationWithDetails>(
        `${this.baseURL}/reservations/${id}/approve`,
        {
          method: 'PUT',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error approving reservation with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Rejeitar uma reserva (para administradores)
   */
  async rejectReservation(
    id: string | number, 
    reason: string
  ): Promise<ReservationWithDetails> {
    try {
      const response = await $fetch<ReservationWithDetails>(
        `${this.baseURL}/reservations/${id}/reject`,
        {
          method: 'PUT',
          body: { rejection_reason: reason },
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error rejecting reservation with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Verificar conflitos de reservas para uma sala
   */
  async checkRoomConflicts(
    roomId: string | number,
    startTime: string,
    endTime: string,
    excludeReservationId?: string | number
  ): Promise<ReservationWithDetails[]> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      queryParams.append('start_time', startTime);
      queryParams.append('end_time', endTime);
      
      if (excludeReservationId) {
        queryParams.append('exclude_id', excludeReservationId.toString());
      }
      
      const response = await $fetch<ReservationWithDetails[]>(
        `${this.baseURL}/rooms/${roomId}/conflicts?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error checking conflicts for room ${roomId}:`, error);
      throw error;
    }
  }

  /**
   * Obter reservas para uma sala específica
   */
  async getRoomReservations(
    roomId: string | number,
    startDate?: string,
    endDate?: string
  ): Promise<ReservationWithDetails[]> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      
      if (startDate) queryParams.append('start_date', startDate);
      if (endDate) queryParams.append('end_date', endDate);
      
      const response = await $fetch<ReservationWithDetails[]>(
        `${this.baseURL}/rooms/${roomId}/reservations?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error fetching reservations for room ${roomId}:`, error);
      throw error;
    }
  }

  /**
   * Buscar salas disponíveis com base em critérios
   */
  async findAvailableRooms(
    startTime: string,
    endTime: string,
    capacity?: number,
    departmentId?: number,
    resources?: number[]
  ): Promise<any[]> {
    try {
      // Construir query params
      const queryParams = new URLSearchParams();
      queryParams.append('start_time', startTime);
      queryParams.append('end_time', endTime);
      
      if (capacity) queryParams.append('min_capacity', capacity.toString());
      if (departmentId) queryParams.append('department_id', departmentId.toString());
      if (resources && resources.length > 0) {
        queryParams.append('resources', resources.join(','));
      }
      
      const response = await $fetch<any[]>(
        `${this.baseURL}/rooms/available?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error finding available rooms:', error);
      throw error;
    }
  }
}

export const reservationsService = new ReservationsService();
