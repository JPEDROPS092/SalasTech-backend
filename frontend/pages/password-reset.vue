<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuth } from '~/composables/use-auth';
import { useRouter, useRoute } from 'vue-router';

const auth = useAuth();
const router = useRouter();
const route = useRoute();
const toast = useToast();

// Check if we have a token in the route (for reset confirmation)
const token = ref(route.query.token as string || '');
const isResetConfirmation = ref(!!token.value);

// Form states
const requestForm = reactive({
  email: ''
});

const resetForm = reactive({
  password: '',
  confirmPassword: ''
});

// Loading state
const loading = ref(false);

// Form validation
const submitted = ref(false);
const emailError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');

// Validate email
const validateEmail = () => {
  if (!requestForm.email) {
    emailError.value = 'Email é obrigatório';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(requestForm.email)) {
    emailError.value = 'Email inválido';
    return false;
  }
  
  emailError.value = '';
  return true;
};

// Validate password
const validatePassword = () => {
  if (!resetForm.password) {
    passwordError.value = 'Senha é obrigatória';
    return false;
  }
  
  if (resetForm.password.length < 8) {
    passwordError.value = 'A senha deve ter pelo menos 8 caracteres';
    return false;
  }
  
  passwordError.value = '';
  return true;
};

// Validate confirm password
const validateConfirmPassword = () => {
  if (!resetForm.confirmPassword) {
    confirmPasswordError.value = 'Confirmação de senha é obrigatória';
    return false;
  }
  
  if (resetForm.password !== resetForm.confirmPassword) {
    confirmPasswordError.value = 'As senhas não coincidem';
    return false;
  }
  
  confirmPasswordError.value = '';
  return true;
};

// Handle password reset request
const handleResetRequest = async () => {
  submitted.value = true;
  
  // Validate form
  const isEmailValid = validateEmail();
  
  if (!isEmailValid) {
    return;
  }
  
  try {
    loading.value = true;
    await auth.requestPasswordReset(requestForm.email);
    
    toast.add({
      severity: 'success',
      summary: 'Solicitação enviada',
      detail: 'Verifique seu email para instruções de redefinição de senha',
      life: 5000
    });
    
    // Clear form
    requestForm.email = '';
    submitted.value = false;
  } catch (error: any) {
    let errorMessage = 'Falha ao solicitar redefinição de senha';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Handle password reset confirmation
const handleResetConfirmation = async () => {
  submitted.value = true;
  
  // Validate form
  const isPasswordValid = validatePassword();
  const isConfirmPasswordValid = validateConfirmPassword();
  
  if (!isPasswordValid || !isConfirmPasswordValid) {
    return;
  }
  
  try {
    loading.value = true;
    await auth.confirmPasswordReset(token.value, resetForm.password);
    
    toast.add({
      severity: 'success',
      summary: 'Senha redefinida',
      detail: 'Sua senha foi redefinida com sucesso. Você pode fazer login agora.',
      life: 3000
    });
    
    // Redirect to login
    router.push('/login');
  } catch (error: any) {
    let errorMessage = 'Falha ao redefinir senha';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.status === 400) {
      errorMessage = 'Token inválido ou expirado';
    }
    
    toast.add({
      severity: 'error',
      summary: 'Erro',
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
</script>

<template>
  <div class="flex flex-column align-items-center justify-content-center min-h-screen bg-blue-50 p-4">
    <div class="surface-card p-5 shadow-2 border-round w-full lg:w-6 md:w-8">
      <div class="text-center mb-5">
        <div class="mb-3">
          <img src="/logo-ifam.png" alt="IFAM Logo" height="80" class="mb-3" />
        </div>
        <div class="text-900 text-3xl font-medium mb-3">
          {{ isResetConfirmation ? 'Redefinir Senha' : 'Recuperar Senha' }}
        </div>
        <span class="text-600 font-medium" v-if="!isResetConfirmation">
          Digite seu email para receber instruções de recuperação de senha
        </span>
        <span class="text-600 font-medium" v-else>
          Digite sua nova senha
        </span>
      </div>
      
      <!-- Password Reset Request Form -->
      <form v-if="!isResetConfirmation" @submit.prevent="handleResetRequest" class="p-fluid">
        <div class="field mb-4">
          <label for="email" class="block text-900 font-medium mb-2">Email</label>
          <div class="p-input-icon-right">
            <i class="pi pi-envelope" />
            <InputText 
              id="email" 
              v-model="requestForm.email" 
              type="email" 
              placeholder="Email" 
              :class="{'p-invalid': submitted && emailError}"
              @blur="validateEmail"
              aria-describedby="email-error"
            />
          </div>
          <small id="email-error" class="p-error">{{ emailError }}</small>
        </div>
        
        <Button 
          type="submit" 
          label="Enviar Instruções" 
          icon="pi pi-envelope" 
          class="w-full mb-4" 
          :loading="loading"
        />
        
        <div class="text-center">
          <a @click="goToLogin" class="font-medium no-underline text-blue-500 cursor-pointer">Voltar para o login</a>
        </div>
      </form>
      
      <!-- Password Reset Confirmation Form -->
      <form v-else @submit.prevent="handleResetConfirmation" class="p-fluid">
        <div class="field mb-4">
          <label for="password" class="block text-900 font-medium mb-2">Nova Senha</label>
          <Password 
            id="password" 
            v-model="resetForm.password" 
            placeholder="Nova Senha" 
            :class="{'p-invalid': submitted && passwordError}"
            :feedback="true"
            :toggleMask="true"
            @blur="validatePassword"
            aria-describedby="password-error"
          />
          <small id="password-error" class="p-error">{{ passwordError }}</small>
        </div>
        
        <div class="field mb-4">
          <label for="confirmPassword" class="block text-900 font-medium mb-2">Confirmar Senha</label>
          <Password 
            id="confirmPassword" 
            v-model="resetForm.confirmPassword" 
            placeholder="Confirmar Senha" 
            :class="{'p-invalid': submitted && confirmPasswordError}"
            :feedback="false"
            :toggleMask="true"
            @blur="validateConfirmPassword"
            aria-describedby="confirm-password-error"
          />
          <small id="confirm-password-error" class="p-error">{{ confirmPasswordError }}</small>
        </div>
        
        <Button 
          type="submit" 
          label="Redefinir Senha" 
          icon="pi pi-check" 
          class="w-full mb-4" 
          :loading="loading"
        />
        
        <div class="text-center">
          <a @click="goToLogin" class="font-medium no-underline text-blue-500 cursor-pointer">Voltar para o login</a>
        </div>
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
