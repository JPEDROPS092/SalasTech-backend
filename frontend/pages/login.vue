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
  email: '',
  password: '',
  rememberMe: false
});

// Loading state
const loading = ref(false);
const showPassword = ref(false);

// Form validation
const submitted = ref(false);
const emailError = ref('');
const passwordError = ref('');

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
  
  passwordError.value = '';
  return true;
};

// Handle login
const handleLogin = async () => {
  submitted.value = true;
  
  // Validate form
  const isEmailValid = validateEmail();
  const isPasswordValid = validatePassword();
  
  if (!isEmailValid || !isPasswordValid) {
    return;
  }
  
  try {
    loading.value = true;
    await auth.login(form.email, form.password);
    
    toast.add({
      severity: 'success',
      summary: 'Login realizado com sucesso',
      detail: 'Redirecionando para o dashboard...',
      life: 3000
    });
    
    // Redirect to dashboard
    router.push('/dashboard');
  } catch (error: any) {
    let errorMessage = 'Falha ao realizar login. Verifique suas credenciais.';
    
    if (error.response?.status === 401) {
      errorMessage = 'Email ou senha incorretos';
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Erro de autenticação',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Handle password reset
const goToPasswordReset = () => {
  router.push('/password-reset');
};

// Handle register
const goToRegister = () => {
  router.push('/register');
};

// Toggle password visibility
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<template>
  <div class="flex flex-column align-items-center justify-content-center min-h-screen bg-blue-50 p-4">
    <div class="surface-card p-5 shadow-2 border-round w-full lg:w-6 md:w-8">
      <div class="text-center mb-5">
        <div class="mb-3">
          <img src="/logo-ifam.png" alt="IFAM Logo" height="80" class="mb-3" />
        </div>
        <div class="text-900 text-3xl font-medium mb-3">Bem-vindo(a) ao IFAM</div>
        <span class="text-600 font-medium">Entre com sua conta para continuar</span>
      </div>
      
      <form @submit.prevent="handleLogin" class="p-fluid">
        <div class="field mb-4">
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
        
        <div class="field mb-4">
          <label for="password" class="block text-900 font-medium mb-2">Senha</label>
          <div class="p-input-icon-right">
            <i 
              :class="showPassword ? 'pi pi-eye-slash' : 'pi pi-eye'" 
              style="cursor: pointer;" 
              @click="togglePasswordVisibility"
            />
            <Password 
              id="password" 
              v-model="form.password" 
              :feedback="false" 
              :toggleMask="true"
              :class="{'p-invalid': submitted && passwordError}"
              placeholder="Senha" 
              @blur="validatePassword"
              aria-describedby="password-error"
            />
          </div>
          <small id="password-error" class="p-error">{{ passwordError }}</small>
        </div>
        
        <div class="flex align-items-center justify-content-between mb-5">
          <div class="flex align-items-center">
            <Checkbox v-model="form.rememberMe" id="rememberme" binary class="mr-2" />
            <label for="rememberme">Lembrar-me</label>
          </div>
          <a @click="goToPasswordReset" class="font-medium no-underline text-blue-500 cursor-pointer">Esqueceu a senha?</a>
        </div>
        
        <Button 
          type="submit" 
          label="Entrar" 
          icon="pi pi-sign-in" 
          class="w-full mb-4" 
          :loading="loading"
        />
        
        <div class="text-center">
          <span class="text-600 font-medium">Não tem uma conta?</span>
          <a @click="goToRegister" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Criar conta</a>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.p-password {
  width: 100%;
}
</style>
