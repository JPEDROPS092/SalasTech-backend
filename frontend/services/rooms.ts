import { useCookie } from 'nuxt/app';

// Tipos
export interface Room {
  id?: number;
  name: string;
  description?: string;
  capacity: number;
  location: string;
  department_id: number;
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE';
  created_at?: string;
  updated_at?: string;
}

export interface RoomWithDetails extends Room {
  department?: {
    id: number;
    name: string;
  };
  resources?: RoomResource[];
}

export interface RoomResource {
  id: number;
  name: string;
  description?: string;
}

export interface Department {
  id: number;
  name: string;
  description?: string;
}

export interface RoomFilters {
  name?: string;
  department_id?: number;
  min_capacity?: number;
  status?: string;
  resources?: number[];
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

class RoomsService {
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
   * Obter todas as salas com paginação e filtros
   */
  async getRooms(
    params: PaginationParams,
    filters?: RoomFilters
  ): Promise<PaginatedResponse<RoomWithDetails>> {
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
        if (filters.name) queryParams.append('name', filters.name);
        if (filters.department_id) queryParams.append('department_id', filters.department_id.toString());
        if (filters.min_capacity) queryParams.append('min_capacity', filters.min_capacity.toString());
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.resources && filters.resources.length > 0) {
          queryParams.append('resources', filters.resources.join(','));
        }
      }
      
      const response = await $fetch<PaginatedResponse<RoomWithDetails>>(
        `${this.baseURL}/rooms?${queryParams.toString()}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching rooms:', error);
      throw error;
    }
  }

  /**
   * Obter uma sala específica por ID
   */
  async getRoom(id: string | number): Promise<RoomWithDetails> {
    try {
      const response = await $fetch<RoomWithDetails>(
        `${this.baseURL}/rooms/${id}`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error fetching room with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Criar uma nova sala
   */
  async createRoom(room: Room, resources?: number[]): Promise<RoomWithDetails> {
    try {
      const payload = {
        ...room,
        resources: resources || []
      };
      
      const response = await $fetch<RoomWithDetails>(
        `${this.baseURL}/rooms`,
        {
          method: 'POST',
          body: payload,
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error creating room:', error);
      throw error;
    }
  }

  /**
   * Atualizar uma sala existente
   */
  async updateRoom(
    id: string | number, 
    room: Partial<Room>,
    resources?: number[]
  ): Promise<RoomWithDetails> {
    try {
      const payload = {
        ...room
      };
      
      // Se recursos forem fornecidos, adicione-os ao payload
      if (resources !== undefined) {
        Object.assign(payload, { resources });
      }
      
      const response = await $fetch<RoomWithDetails>(
        `${this.baseURL}/rooms/${id}`,
        {
          method: 'PUT',
          body: payload,
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error(`Error updating room with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Excluir uma sala
   */
  async deleteRoom(id: string | number): Promise<void> {
    try {
      await $fetch(
        `${this.baseURL}/rooms/${id}`,
        {
          method: 'DELETE',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
    } catch (error) {
      console.error(`Error deleting room with id ${id}:`, error);
      throw error;
    }
  }

  /**
   * Obter todos os departamentos
   */
  async getDepartments(): Promise<Department[]> {
    try {
      const response = await $fetch<Department[]>(
        `${this.baseURL}/departments`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching departments:', error);
      throw error;
    }
  }

  /**
   * Obter todos os recursos disponíveis para salas
   */
  async getRoomResources(): Promise<RoomResource[]> {
    try {
      const response = await $fetch<RoomResource[]>(
        `${this.baseURL}/room-resources`,
        {
          method: 'GET',
          headers: { ...this.headers, ...this.getAuthHeader() }
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching room resources:', error);
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
  ): Promise<RoomWithDetails[]> {
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
      
      const response = await $fetch<RoomWithDetails[]>(
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

export const roomsService = new RoomsService();
