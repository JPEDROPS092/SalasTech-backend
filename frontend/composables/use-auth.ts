import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import api from '~/services/api';

// Define user type
interface User {
  id: number;
  name: string;
  surname: string;
  email: string;
  role: string;
  department_id?: number;
  updated_at: string;
  created_at: string;
}

// Create auth store using Pinia
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN' || user.value?.role === 'ADMINISTRADOR');
  const isManager = computed(() => user.value?.role === 'GESTOR');
  
  // Check if user has admin privileges
  const hasAdminAccess = computed(() => isAdmin.value || isManager.value);
  
  // Get full name
  const fullName = computed(() => {
    if (!user.value) return '';
    return `${user.value.name} ${user.value.surname}`;
  });
  
  // Login function
  async function login(email: string, password: string) {
    try {
      const response = await api.login(email, password);
      user.value = response.user;
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }
  
  // Register function
  async function register(userData: any) {
    try {
      return await api.register(userData);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }
  
  // Logout function
  async function logout() {
    try {
      await api.logout();
      user.value = null;
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }
  
  // Initialize user data from API or local storage
  async function initAuth() {
    const token = useCookie('auth_token');
    
    if (token.value) {
      try {
        user.value = await api.getCurrentUser();
      } catch (error) {
        // If token is invalid, clear it
        token.value = null;
        user.value = null;
      }
    }
  }
  
  // Reset password request
  async function requestPasswordReset(email: string) {
    return await api.resetPassword(email);
  }
  
  // Confirm password reset
  async function confirmPasswordReset(token: string, password: string) {
    return await api.confirmResetPassword(token, password);
  }
  
  // Update password
  async function updatePassword(oldPassword: string, newPassword: string) {
    return await api.updatePassword(oldPassword, newPassword);
  }
  
  return {
    user,
    isAuthenticated,
    isAdmin,
    isManager,
    hasAdminAccess,
    fullName,
    login,
    register,
    logout,
    initAuth,
    requestPasswordReset,
    confirmPasswordReset,
    updatePassword
  };
});

// Composable to use the auth store
export function useAuth() {
  return useAuthStore();
}
