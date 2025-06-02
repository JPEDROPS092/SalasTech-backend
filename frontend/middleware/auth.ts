import { useAuth } from '~/composables/use-auth';

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuth();
  const isAuthenticated = auth.isAuthenticated;
  
  // Se o usuário não estiver autenticado e a rota não for pública, redirecionar para login
  if (!isAuthenticated && !to.meta.public) {
    return navigateTo('/login');
  }
  
  // Se a rota requer papel de admin e o usuário não é admin, redirecionar para dashboard
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return navigateTo('/dashboard');
  }
});
