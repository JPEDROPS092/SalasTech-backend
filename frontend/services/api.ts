import { useCookie } from 'nuxt/app';

// Define types for the API responses and requests
interface UserDTO {
  id: number;
  name: string;
  surname: string;
  email: string;
  role: string;
  department_id?: number;
  updated_at: string;
  created_at: string;
}

interface UserCreateDTO {
  name: string;
  surname: string;
  email: string;
  password: string;
  department_id?: number;
  role?: string;
}

interface UserLoginDTO {
  email: string;
  password: string;
}

interface UserUpdatePassDTO {
  old_password: string;
  new_password: string;
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// API service for backend communication
const api = {
  // Base API URL - adjust based on your environment
  baseURL: 'http://localhost:8000/api',
  
  // Default headers
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  
  // Authentication
  async login(email: string, password: string): Promise<{ token: string; user: UserDTO }> {
    try {
      const response = await $fetch<string>(`${this.baseURL}/auth/login`, {
        method: 'POST',
        body: { email, password } as UserLoginDTO,
        headers: this.headers
      });
      
      // Store token in cookie
      const token = useCookie('auth_token');
      token.value = response;
      
      // Get user data
      const user = await this.getCurrentUser();
      return { token: response, user };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  async register(userData: UserCreateDTO): Promise<UserDTO> {
    try {
      const response = await $fetch<UserDTO>(`${this.baseURL}/auth/register`, {
        method: 'POST',
        body: userData,
        headers: this.headers
      });
      return response;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  async logout(): Promise<void> {
    try {
      await $fetch(`${this.baseURL}/auth/logout`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });
      
      // Clear token
      const token = useCookie('auth_token');
      token.value = null;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },
  
  async getCurrentUser(): Promise<UserDTO> {
    try {
      const response = await $fetch<UserDTO>(`${this.baseURL}/user/me`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });
      return response;
    } catch (error) {
      console.error('Get user error:', error);
      throw error;
    }
  },
  
  async resetPassword(email: string): Promise<ApiResponse<any>> {
    try {
      const response = await $fetch<ApiResponse<any>>(`${this.baseURL}/auth/password/reset`, {
        method: 'POST',
        body: { email },
        headers: this.headers
      });
      return response;
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  },
  
  async confirmResetPassword(token: string, password: string): Promise<ApiResponse<any>> {
    try {
      const response = await $fetch<ApiResponse<any>>(`${this.baseURL}/auth/password/reset/${token}`, {
        method: 'POST',
        body: { password },
        headers: this.headers
      });
      return response;
    } catch (error) {
      console.error('Confirm reset password error:', error);
      throw error;
    }
  },
  
  async updatePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      await $fetch(`${this.baseURL}/auth/password/update`, {
        method: 'PUT',
        body: { old_password: oldPassword, new_password: newPassword } as UserUpdatePassDTO,
        headers: this.getAuthHeaders()
      });
    } catch (error) {
      console.error('Update password error:', error);
      throw error;
    }
  },
  
  // Users
  async getAllUsers(limit: number = 1000, offset: number = 0): Promise<UserDTO[]> {
    try {
      const response = await $fetch<UserDTO[]>(`${this.baseURL}/user/all?limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });
      return response;
    } catch (error) {
      console.error('Get all users error:', error);
      throw error;
    }
  },
  
  async getUserById(id: number): Promise<UserDTO> {
    try {
      const response = await $fetch<UserDTO>(`${this.baseURL}/user/${id}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });
      return response;
    } catch (error) {
      console.error(`Get user ${id} error:`, error);
      throw error;
    }
  },
  
  // Helper methods
  getAuthHeaders(): Record<string, string> {
    const token = useCookie('auth_token');
    return {
      ...this.headers,
      'Authorization': `Bearer ${token.value}`
    };
  }
};

export default api;
