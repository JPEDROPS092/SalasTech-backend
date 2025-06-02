<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuth } from '~/composables/use-auth';
import api from '~/services/api';

const auth = useAuth();
const toast = useToast();

// User data
const user = ref({
  id: 0,
  name: '',
  surname: '',
  email: '',
  role: '',
  department_id: null,
  department_name: '',
  created_at: '',
  updated_at: ''
});

// Form states
const profileForm = reactive({
  name: '',
  surname: '',
  email: '',
  department_id: null
});

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// Loading states
const loading = ref({
  profile: false,
  password: false,
  data: false
});

// Form validation
const profileSubmitted = ref(false);
const passwordSubmitted = ref(false);

const nameError = ref('');
const surnameError = ref('');
const emailError = ref('');
const currentPasswordError = ref('');
const newPasswordError = ref('');
const confirmPasswordError = ref('');

// Tabs
const activeTab = ref(0);

// Departments
const departments = ref([]);

// Fetch user data
const fetchUserData = async () => {
  try {
    loading.value.data = true;
    const userData = await auth.user;
    
    if (userData) {
      user.value = { ...userData };
      
      // Initialize profile form
      profileForm.name = userData.name;
      profileForm.surname = userData.surname;
      profileForm.email = userData.email;
      profileForm.department_id = userData.department_id;
      
      // Fetch department name if department_id exists
      if (userData.department_id) {
        // Implement API call to get department name
        // const departmentData = await api.getDepartmentById(userData.department_id);
        // user.value.department_name = departmentData.name;
        
        // Mock data for now
        user.value.department_name = 'Departamento de TI';
      }
    }
  } catch (error) {
    console.error('Error fetching user data:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível carregar os dados do usuário',
      life: 3000
    });
  } finally {
    loading.value.data = false;
  }
};

// Fetch departments
const fetchDepartments = async () => {
  try {
    // Implement API call to get departments
    // const departmentsData = await api.getDepartments();
    // departments.value = departmentsData;
    
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

// Validate name
const validateName = () => {
  if (!profileForm.name.trim()) {
    nameError.value = 'Nome é obrigatório';
    return false;
  }
  
  nameError.value = '';
  return true;
};

// Validate surname
const validateSurname = () => {
  if (!profileForm.surname.trim()) {
    surnameError.value = 'Sobrenome é obrigatório';
    return false;
  }
  
  surnameError.value = '';
  return true;
};

// Validate email
const validateEmail = () => {
  if (!profileForm.email) {
    emailError.value = 'Email é obrigatório';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(profileForm.email)) {
    emailError.value = 'Email inválido';
    return false;
  }
  
  emailError.value = '';
  return true;
};

// Validate current password
const validateCurrentPassword = () => {
  if (!passwordForm.currentPassword) {
    currentPasswordError.value = 'Senha atual é obrigatória';
    return false;
  }
  
  currentPasswordError.value = '';
  return true;
};

// Validate new password
const validateNewPassword = () => {
  if (!passwordForm.newPassword) {
    newPasswordError.value = 'Nova senha é obrigatória';
    return false;
  }
  
  if (passwordForm.newPassword.length < 8) {
    newPasswordError.value = 'A senha deve ter pelo menos 8 caracteres';
    return false;
  }
  
  if (passwordForm.newPassword === passwordForm.currentPassword) {
    newPasswordError.value = 'A nova senha deve ser diferente da senha atual';
    return false;
  }
  
  newPasswordError.value = '';
  return true;
};

// Validate confirm password
const validateConfirmPassword = () => {
  if (!passwordForm.confirmPassword) {
    confirmPasswordError.value = 'Confirmação de senha é obrigatória';
    return false;
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    confirmPasswordError.value = 'As senhas não coincidem';
    return false;
  }
  
  confirmPasswordError.value = '';
  return true;
};

// Update profile
const updateProfile = async () => {
  profileSubmitted.value = true;
  
  // Validate form
  const isNameValid = validateName();
  const isSurnameValid = validateSurname();
  const isEmailValid = validateEmail();
  
  if (!isNameValid || !isSurnameValid || !isEmailValid) {
    return;
  }
  
  try {
    loading.value.profile = true;
    
    // Create user data object
    const userData = {
      name: profileForm.name,
      surname: profileForm.surname,
      email: profileForm.email,
      department_id: profileForm.department_id
    };
    
    // Implement API call to update user profile
    // await api.updateUserProfile(user.value.id, userData);
    
    // Update local user data
    user.value = {
      ...user.value,
      ...userData
    };
    
    // Update auth store user data
    auth.user = user.value;
    
    toast.add({
      severity: 'success',
      summary: 'Perfil atualizado',
      detail: 'Suas informações foram atualizadas com sucesso',
      life: 3000
    });
    
    profileSubmitted.value = false;
  } catch (error) {
    console.error('Error updating profile:', error);
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: 'Não foi possível atualizar o perfil',
      life: 3000
    });
  } finally {
    loading.value.profile = false;
  }
};

// Update password
const updatePassword = async () => {
  passwordSubmitted.value = true;
  
  // Validate form
  const isCurrentPasswordValid = validateCurrentPassword();
  const isNewPasswordValid = validateNewPassword();
  const isConfirmPasswordValid = validateConfirmPassword();
  
  if (!isCurrentPasswordValid || !isNewPasswordValid || !isConfirmPasswordValid) {
    return;
  }
  
  try {
    loading.value.password = true;
    
    // Implement API call to update password
    await auth.updatePassword(passwordForm.currentPassword, passwordForm.newPassword);
    
    toast.add({
      severity: 'success',
      summary: 'Senha atualizada',
      detail: 'Sua senha foi atualizada com sucesso',
      life: 3000
    });
    
    // Reset form
    passwordForm.currentPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';
    passwordSubmitted.value = false;
  } catch (error) {
    console.error('Error updating password:', error);
    
    let errorMessage = 'Não foi possível atualizar a senha';
    
    if (error.response?.status === 401) {
      errorMessage = 'Senha atual incorreta';
      currentPasswordError.value = errorMessage;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: errorMessage,
      life: 3000
    });
  } finally {
    loading.value.password = false;
  }
};

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

// Get role display name
const getRoleDisplayName = (role) => {
  switch (role) {
    case 'ADMIN':
    case 'ADMINISTRADOR':
      return 'Administrador';
    case 'GESTOR':
      return 'Gestor';
    case 'USER':
      return 'Usuário';
    default:
      return role;
  }
};

// Initialize component
onMounted(async () => {
  await fetchUserData();
  await fetchDepartments();
});
</script>

<template>
  <div class="grid">
    <div class="col-12">
      <div class="card">
        <h5>Meu Perfil</h5>
        
        <div v-if="loading.data" class="flex justify-content-center">
          <ProgressSpinner />
        </div>
        
        <div v-else class="grid">
          <!-- User info card -->
          <div class="col-12 md:col-4">
            <div class="card mb-0">
              <div class="flex flex-column align-items-center">
                <Avatar :label="user.name.charAt(0) + user.surname.charAt(0)" class="mb-3" size="xlarge" style="background-color:var(--primary-color); color: #ffffff" />
                <div class="text-2xl font-bold mb-2">{{ user.name }} {{ user.surname }}</div>
                <div class="text-500 mb-3">{{ user.email }}</div>
                <Tag :value="getRoleDisplayName(user.role)" severity="info" class="mb-3" />
                
                <div class="card w-full mt-3">
                  <ul class="list-none p-0 m-0">
                    <li class="flex align-items-center py-2 border-bottom-1 surface-border">
                      <span class="text-500 w-6 md:w-4 font-medium">Departamento</span>
                      <span class="font-medium">{{ user.department_name || 'Não definido' }}</span>
                    </li>
                    <li class="flex align-items-center py-2 border-bottom-1 surface-border">
                      <span class="text-500 w-6 md:w-4 font-medium">Função</span>
                      <span class="font-medium">{{ getRoleDisplayName(user.role) }}</span>
                    </li>
                    <li class="flex align-items-center py-2 border-bottom-1 surface-border">
                      <span class="text-500 w-6 md:w-4 font-medium">Membro desde</span>
                      <span class="font-medium">{{ formatDate(user.created_at) }}</span>
                    </li>
                    <li class="flex align-items-center py-2">
                      <span class="text-500 w-6 md:w-4 font-medium">Última atualização</span>
                      <span class="font-medium">{{ formatDate(user.updated_at) }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Profile settings -->
          <div class="col-12 md:col-8">
            <TabView v-model:activeIndex="activeTab">
              <!-- Profile tab -->
              <TabPanel header="Informações Pessoais">
                <form @submit.prevent="updateProfile" class="p-fluid">
                  <div class="grid formgrid">
                    <div class="field col-12 md:col-6 mb-4">
                      <label for="name" class="block text-900 font-medium mb-2">Nome</label>
                      <InputText 
                        id="name" 
                        v-model="profileForm.name" 
                        type="text" 
                        placeholder="Nome" 
                        :class="{'p-invalid': profileSubmitted && nameError}"
                        @blur="validateName"
                        aria-describedby="name-error"
                      />
                      <small id="name-error" class="p-error">{{ nameError }}</small>
                    </div>
                    
                    <div class="field col-12 md:col-6 mb-4">
                      <label for="surname" class="block text-900 font-medium mb-2">Sobrenome</label>
                      <InputText 
                        id="surname" 
                        v-model="profileForm.surname" 
                        type="text" 
                        placeholder="Sobrenome" 
                        :class="{'p-invalid': profileSubmitted && surnameError}"
                        @blur="validateSurname"
                        aria-describedby="surname-error"
                      />
                      <small id="surname-error" class="p-error">{{ surnameError }}</small>
                    </div>
                    
                    <div class="field col-12 mb-4">
                      <label for="email" class="block text-900 font-medium mb-2">Email</label>
                      <div class="p-input-icon-right">
                        <i class="pi pi-envelope" />
                        <InputText 
                          id="email" 
                          v-model="profileForm.email" 
                          type="email" 
                          placeholder="Email" 
                          :class="{'p-invalid': profileSubmitted && emailError}"
                          @blur="validateEmail"
                          aria-describedby="email-error"
                        />
                      </div>
                      <small id="email-error" class="p-error">{{ emailError }}</small>
                    </div>
                    
                    <div class="field col-12 mb-4">
                      <label for="department" class="block text-900 font-medium mb-2">Departamento</label>
                      <Dropdown 
                        id="department" 
                        v-model="profileForm.department_id" 
                        :options="departments" 
                        optionLabel="name" 
                        optionValue="id"
                        placeholder="Selecione um departamento" 
                        class="w-full"
                      />
                    </div>
                    
                    <div class="field col-12">
                      <Button 
                        type="submit" 
                        label="Salvar Alterações" 
                        icon="pi pi-check" 
                        class="w-auto" 
                        :loading="loading.profile"
                      />
                    </div>
                  </div>
                </form>
              </TabPanel>
              
              <!-- Password tab -->
              <TabPanel header="Alterar Senha">
                <form @submit.prevent="updatePassword" class="p-fluid">
                  <div class="field mb-4">
                    <label for="currentPassword" class="block text-900 font-medium mb-2">Senha Atual</label>
                    <Password 
                      id="currentPassword" 
                      v-model="passwordForm.currentPassword" 
                      placeholder="Senha Atual" 
                      :class="{'p-invalid': passwordSubmitted && currentPasswordError}"
                      :feedback="false"
                      :toggleMask="true"
                      @blur="validateCurrentPassword"
                      aria-describedby="current-password-error"
                    />
                    <small id="current-password-error" class="p-error">{{ currentPasswordError }}</small>
                  </div>
                  
                  <div class="field mb-4">
                    <label for="newPassword" class="block text-900 font-medium mb-2">Nova Senha</label>
                    <Password 
                      id="newPassword" 
                      v-model="passwordForm.newPassword" 
                      placeholder="Nova Senha" 
                      :class="{'p-invalid': passwordSubmitted && newPasswordError}"
                      :feedback="true"
                      :toggleMask="true"
                      @blur="validateNewPassword"
                      aria-describedby="new-password-error"
                    />
                    <small id="new-password-error" class="p-error">{{ newPasswordError }}</small>
                  </div>
                  
                  <div class="field mb-4">
                    <label for="confirmPassword" class="block text-900 font-medium mb-2">Confirmar Senha</label>
                    <Password 
                      id="confirmPassword" 
                      v-model="passwordForm.confirmPassword" 
                      placeholder="Confirmar Senha" 
                      :class="{'p-invalid': passwordSubmitted && confirmPasswordError}"
                      :feedback="false"
                      :toggleMask="true"
                      @blur="validateConfirmPassword"
                      aria-describedby="confirm-password-error"
                    />
                    <small id="confirm-password-error" class="p-error">{{ confirmPasswordError }}</small>
                  </div>
                  
                  <div class="field">
                    <Button 
                      type="submit" 
                      label="Atualizar Senha" 
                      icon="pi pi-lock" 
                      class="w-auto" 
                      :loading="loading.password"
                    />
                  </div>
                </form>
              </TabPanel>
              
              <!-- Notifications tab -->
              <TabPanel header="Notificações">
                <div class="field-checkbox mb-3">
                  <Checkbox id="notification1" name="notification1" value="email" :binary="true" v-model="true" />
                  <label for="notification1" class="ml-2">Receber notificações por email</label>
                </div>
                
                <div class="field-checkbox mb-3">
                  <Checkbox id="notification2" name="notification2" value="reservations" :binary="true" v-model="true" />
                  <label for="notification2" class="ml-2">Notificar sobre atualizações de reservas</label>
                </div>
                
                <div class="field-checkbox mb-3">
                  <Checkbox id="notification3" name="notification3" value="system" :binary="true" v-model="true" />
                  <label for="notification3" class="ml-2">Notificações do sistema</label>
                </div>
                
                <div class="field-checkbox mb-3">
                  <Checkbox id="notification4" name="notification4" value="marketing" :binary="true" v-model="false" />
                  <label for="notification4" class="ml-2">Receber informações e novidades</label>
                </div>
                
                <div class="field mt-4">
                  <Button label="Salvar Preferências" icon="pi pi-save" class="w-auto" />
                </div>
              </TabPanel>
            </TabView>
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

.p-tabview .p-tabview-nav {
  border-bottom: 1px solid var(--surface-border);
}

.p-tabview .p-tabview-nav li .p-tabview-nav-link {
  border: none;
  color: var(--text-color-secondary);
  padding: 1rem;
}

.p-tabview .p-tabview-nav li.p-highlight .p-tabview-nav-link {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.p-password {
  width: 100%;
}
</style>
