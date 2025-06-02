<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuth } from '~/composables/use-auth';
import { useRouter } from 'vue-router';

const auth = useAuth();
const router = useRouter();
const toast = useToast();

// Form state
const form = reactive({
  name: '',
  surname: '',
  email: '',
  password: '',
  confirmPassword: '',
  department_id: null,
  role: 'USER',
  terms: false
});

// Loading state
const loading = ref(false);
const departments = ref([]);
const roles = ref([
  { name: 'Usuário', value: 'USER' },
  { name: 'Gestor', value: 'GESTOR' }
]);

// Form validation
const submitted = ref(false);
const nameError = ref('');
const surnameError = ref('');
const emailError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');
const termsError = ref('');

// Fetch departments
const fetchDepartments = async () => {
  try {
    // Implement API call to get departments
    // departments.value = await api.getDepartments();
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
  if (!form.name.trim()) {
    nameError.value = 'Nome é obrigatório';
    return false;
  }
  
  nameError.value = '';
  return true;
};

// Validate surname
const validateSurname = () => {
  if (!form.surname.trim()) {
    surnameError.value = 'Sobrenome é obrigatório';
    return false;
  }
  
  surnameError.value = '';
  return true;
};

// Validate email
const validateEmail = () => {
  if (!form.email) {
    emailError.value = 'Email é obrigatório';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    emailError.value = 'Email inválido';
    return false;
  }
  
  emailError.value = '';
  return true;
};

// Validate password
const validatePassword = () => {
  if (!form.password) {
    passwordError.value = 'Senha é obrigatória';
    return false;
  }
  
  if (form.password.length < 8) {
    passwordError.value = 'A senha deve ter pelo menos 8 caracteres';
    return false;
  }
  
  passwordError.value = '';
  return true;
};

// Validate confirm password
const validateConfirmPassword = () => {
  if (!form.confirmPassword) {
    confirmPasswordError.value = 'Confirmação de senha é obrigatória';
    return false;
  }
  
  if (form.password !== form.confirmPassword) {
    confirmPasswordError.value = 'As senhas não coincidem';
    return false;
  }
  
  confirmPasswordError.value = '';
  return true;
};

// Validate terms
const validateTerms = () => {
  if (!form.terms) {
    termsError.value = 'Você deve aceitar os termos e condições';
    return false;
  }
  
  termsError.value = '';
  return true;
};

// Handle register
const handleRegister = async () => {
  submitted.value = true;
  
  // Validate form
  const isNameValid = validateName();
  const isSurnameValid = validateSurname();
  const isEmailValid = validateEmail();
  const isPasswordValid = validatePassword();
  const isConfirmPasswordValid = validateConfirmPassword();
  const isTermsValid = validateTerms();
  
  if (!isNameValid || !isSurnameValid || !isEmailValid || !isPasswordValid || !isConfirmPasswordValid || !isTermsValid) {
    return;
  }
  
  try {
    loading.value = true;
    
    // Create user object from form
    const userData = {
      name: form.name,
      surname: form.surname,
      email: form.email,
      password: form.password,
      department_id: form.department_id,
      role: form.role
    };
    
    await auth.register(userData);
    
    toast.add({
      severity: 'success',
      summary: 'Registro realizado com sucesso',
      detail: 'Sua conta foi criada. Você pode fazer login agora.',
      life: 3000
    });
    
    // Redirect to login
    router.push('/login');
  } catch (error: any) {
    let errorMessage = 'Falha ao registrar. Por favor, tente novamente.';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.status === 409) {
      errorMessage = 'Este email já está em uso';
    }
    
    toast.add({
      severity: 'error',
      summary: 'Erro no registro',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Handle login
const goToLogin = () => {
  router.push('/login');
};

// Fetch departments on component mount
onMounted(() => {
  fetchDepartments();
});
</script>

<template>
  <div class="flex flex-column align-items-center justify-content-center min-h-screen bg-blue-50 p-4">
    <div class="surface-card p-5 shadow-2 border-round w-full lg:w-6 md:w-8">
      <div class="text-center mb-5">
        <div class="mb-3">
          <img src="/logo-ifam.png" alt="IFAM Logo" height="80" class="mb-3" />
        </div>
        <div class="text-900 text-3xl font-medium mb-3">Criar uma Conta</div>
        <span class="text-600 font-medium">Já tem uma conta? <a @click="goToLogin" class="font-medium no-underline text-blue-500 cursor-pointer">Entrar</a></span>
      </div>
      
      <form @submit.prevent="handleRegister" class="p-fluid">
        <div class="grid formgrid">
          <div class="field col-12 md:col-6 mb-4">
            <label for="name" class="block text-900 font-medium mb-2">Nome</label>
            <InputText 
              id="name" 
              v-model="form.name" 
              type="text" 
              placeholder="Nome" 
              :class="{'p-invalid': submitted && nameError}"
              @blur="validateName"
              aria-describedby="name-error"
            />
            <small id="name-error" class="p-error">{{ nameError }}</small>
          </div>
          
          <div class="field col-12 md:col-6 mb-4">
            <label for="surname" class="block text-900 font-medium mb-2">Sobrenome</label>
            <InputText 
              id="surname" 
              v-model="form.surname" 
              type="text" 
              placeholder="Sobrenome" 
              :class="{'p-invalid': submitted && surnameError}"
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
                v-model="form.email" 
                type="email" 
                placeholder="Email" 
                :class="{'p-invalid': submitted && emailError}"
                @blur="validateEmail"
                aria-describedby="email-error"
              />
            </div>
            <small id="email-error" class="p-error">{{ emailError }}</small>
          </div>
          
          <div class="field col-12 md:col-6 mb-4">
            <label for="password" class="block text-900 font-medium mb-2">Senha</label>
            <Password 
              id="password" 
              v-model="form.password" 
              placeholder="Senha" 
              :class="{'p-invalid': submitted && passwordError}"
              :feedback="true"
              :toggleMask="true"
              @blur="validatePassword"
              aria-describedby="password-error"
            />
            <small id="password-error" class="p-error">{{ passwordError }}</small>
          </div>
          
          <div class="field col-12 md:col-6 mb-4">
            <label for="confirmPassword" class="block text-900 font-medium mb-2">Confirmar Senha</label>
            <Password 
              id="confirmPassword" 
              v-model="form.confirmPassword" 
              placeholder="Confirmar Senha" 
              :class="{'p-invalid': submitted && confirmPasswordError}"
              :feedback="false"
              :toggleMask="true"
              @blur="validateConfirmPassword"
              aria-describedby="confirm-password-error"
            />
            <small id="confirm-password-error" class="p-error">{{ confirmPasswordError }}</small>
          </div>
          
          <div class="field col-12 md:col-6 mb-4">
            <label for="department" class="block text-900 font-medium mb-2">Departamento</label>
            <Dropdown 
              id="department" 
              v-model="form.department_id" 
              :options="departments" 
              optionLabel="name" 
              optionValue="id"
              placeholder="Selecione um departamento" 
              class="w-full"
            />
          </div>
          
          <div class="field col-12 md:col-6 mb-4">
            <label for="role" class="block text-900 font-medium mb-2">Função</label>
            <Dropdown 
              id="role" 
              v-model="form.role" 
              :options="roles" 
              optionLabel="name" 
              optionValue="value"
              placeholder="Selecione uma função" 
              class="w-full"
            />
          </div>
          
          <div class="field-checkbox col-12 mb-4">
            <Checkbox 
              id="terms" 
              v-model="form.terms" 
              :binary="true" 
              :class="{'p-invalid': submitted && termsError}"
              aria-describedby="terms-error"
            />
            <label for="terms" class="ml-2">Eu concordo com os <a href="#" class="text-primary">termos e condições</a></label>
            <div>
              <small id="terms-error" class="p-error">{{ termsError }}</small>
            </div>
          </div>
        </div>
        
        <Button 
          type="submit" 
          label="Criar Conta" 
          icon="pi pi-user-plus" 
          class="w-full mb-4" 
          :loading="loading"
        />
      </form>
    </div>
  </div>
</template>

<style scoped>
.p-password {
  width: 100%;
}

a {
  cursor: pointer;
}
</style>
