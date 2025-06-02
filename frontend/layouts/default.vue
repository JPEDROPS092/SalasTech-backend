<template>
  <div class="layout-wrapper">
    <AppTopbar />
    
    <div class="layout-content-wrapper">
      <div class="layout-sidebar">
        <div class="sidebar-header">
          <img src="/logo-ifam.png" alt="IFAM Logo" height="40" />
          <h3>IFAM</h3>
        </div>
        
        <div class="sidebar-menu">
          <ul>
            <li>
              <NuxtLink to="/dashboard" class="p-ripple">
                <i class="pi pi-home"></i>
                <span>Dashboard</span>
              </NuxtLink>
            </li>
            <li v-if="auth.hasAdminAccess">
              <NuxtLink to="/admin/users" class="p-ripple">
                <i class="pi pi-users"></i>
                <span>Usuários</span>
              </NuxtLink>
            </li>
            <li v-if="auth.hasAdminAccess">
              <NuxtLink to="/admin/departments" class="p-ripple">
                <i class="pi pi-building"></i>
                <span>Departamentos</span>
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/rooms" class="p-ripple">
                <i class="pi pi-th-large"></i>
                <span>Salas</span>
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/rooms/available" class="p-ripple">
                <i class="pi pi-search"></i>
                <span>Buscar Salas</span>
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/reservations" class="p-ripple">
                <i class="pi pi-calendar"></i>
                <span>Reservas</span>
              </NuxtLink>
            </li>
            <li v-if="auth.hasAdminAccess">
              <NuxtLink to="/admin/reports" class="p-ripple">
                <i class="pi pi-chart-bar"></i>
                <span>Relatórios</span>
              </NuxtLink>
            </li>
            <li>
              <NuxtLink to="/profile" class="p-ripple">
                <i class="pi pi-user"></i>
                <span>Perfil</span>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
      
      <div class="layout-content">
        <div class="content-wrapper">
          <slot />
        </div>
        <AppFooter />
      </div>
    </div>
    
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuth } from '~/composables/use-auth';

const auth = useAuth();

onMounted(async () => {
  await auth.initAuth();
});
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--surface-ground);
}

.layout-content-wrapper {
  display: flex;
  flex: 1;
  margin-top: 4rem;
}

.layout-sidebar {
  width: 250px;
  background-color: var(--surface-card);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  left: 0;
  top: 4rem;
  height: calc(100vh - 4rem);
  z-index: 999;
  overflow-y: auto;
  transition: transform 0.3s;
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--surface-border);
}

.sidebar-header h3 {
  margin: 0 0 0 0.5rem;
  color: var(--primary-color);
}

.sidebar-menu {
  padding: 1rem 0;
}

.sidebar-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sidebar-menu li {
  margin-bottom: 0.25rem;
}

.sidebar-menu a {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: var(--text-color);
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.sidebar-menu a:hover {
  background-color: var(--surface-hover);
}

.sidebar-menu a.router-link-active {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.sidebar-menu i {
  margin-right: 0.5rem;
  font-size: 1.25rem;
}

.layout-content {
  margin-left: 250px;
  flex: 1;
  padding: 1rem;
  transition: margin-left 0.3s;
}

.content-wrapper {
  background-color: var(--surface-card);
  border-radius: 4px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  min-height: calc(100vh - 10rem);
}

@media screen and (max-width: 991px) {
  .layout-sidebar {
    transform: translateX(-100%);
  }
  
  .layout-sidebar.active {
    transform: translateX(0);
  }
  
  .layout-content {
    margin-left: 0;
  }
}
</style>
