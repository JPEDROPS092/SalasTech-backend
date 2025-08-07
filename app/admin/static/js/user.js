/**
 * SalasTech - User Interface JavaScript
 * Funcionalidades específicas para a interface de usuário
 */

// Configuração global
const API_BASE = '/api';

// Utilitários
const Utils = {
    /**
     * Formatar data para exibição
     */
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('pt-BR');
    },

    /**
     * Formatar horário para exibição
     */
    formatTime: function(date) {
        return new Date(date).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Mostrar notificação
     */
    showNotification: function(message, type = 'info') {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const icon = type === 'error' ? 'fa-exclamation-triangle' : 
                    type === 'success' ? 'fa-check-circle' : 
                    type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle';
        
        const alertHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas ${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Inserir no início do main-content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertAdjacentHTML('afterbegin', alertHTML);
            
            // Auto-remover após 5 segundos
            setTimeout(() => {
                const alert = mainContent.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    },

    /**
     * Fazer requisição AJAX
     */
    request: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }
};

// Funcionalidades de Reservas
const Reservations = {
    /**
     * Cancelar reserva
     */
    cancel: async function(reservationId, callback) {
        if (!confirm('Tem certeza que deseja cancelar esta reserva?')) {
            return;
        }

        try {
            const result = await Utils.request(`${API_BASE}/reservations/${reservationId}`, {
                method: 'DELETE'
            });

            Utils.showNotification('Reserva cancelada com sucesso!', 'success');
            
            if (callback) {
                callback(result);
            } else {
                // Recarregar página após um breve delay
                setTimeout(() => location.reload(), 1000);
            }
        } catch (error) {
            Utils.showNotification(`Erro ao cancelar reserva: ${error.message}`, 'error');
        }
    },

    /**
     * Verificar disponibilidade
     */
    checkAvailability: async function(roomId, date, startTime, endTime) {
        try {
            const result = await Utils.request(`${API_BASE}/check-availability`, {
                method: 'POST',
                body: JSON.stringify({
                    room_id: roomId,
                    date: date,
                    start_time: startTime,
                    end_time: endTime
                })
            });

            return result;
        } catch (error) {
            console.error('Erro ao verificar disponibilidade:', error);
            return { available: false, message: 'Erro ao verificar disponibilidade' };
        }
    }
};

// Funcionalidades de Interface
const UI = {
    /**
     * Inicializar componentes da interface
     */
    init: function() {
        this.initTooltips();
        this.initDateInputs();
        this.initTimeValidation();
        this.initSearchFilters();
    },

    /**
     * Inicializar tooltips
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Configurar inputs de data
     */
    initDateInputs: function() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];
        
        dateInputs.forEach(input => {
            if (!input.hasAttribute('min')) {
                input.setAttribute('min', today);
            }
        });
    },

    /**
     * Validação de horários
     */
    initTimeValidation: function() {
        const startTimeInputs = document.querySelectorAll('input[name="start_time"]');
        
        startTimeInputs.forEach(startInput => {
            startInput.addEventListener('change', function() {
                const endInput = document.querySelector('input[name="end_time"]');
                if (!endInput) return;
                
                const startTime = this.value;
                if (startTime) {
                    const [hours, minutes] = startTime.split(':');
                    const endHours = parseInt(hours) + 1;
                    const minEndTime = `${endHours.toString().padStart(2, '0')}:${minutes}`;
                    
                    endInput.setAttribute('min', minEndTime);
                    
                    if (endInput.value && endInput.value <= startTime) {
                        endInput.value = minEndTime;
                    }
                }
            });
        });
    },

    /**
     * Filtros de busca com auto-submit
     */
    initSearchFilters: function() {
        const searchForm = document.querySelector('form[method="get"]');
        if (!searchForm) return;

        const autoSubmitInputs = searchForm.querySelectorAll('input[type="date"], input[type="time"], select');
        
        autoSubmitInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Delay para permitir múltiplas seleções
                clearTimeout(this.submitTimer);
                this.submitTimer = setTimeout(() => {
                    if (this.value) {
                        searchForm.submit();
                    }
                }, 500);
            });
        });
    },

    /**
     * Atualizar contador de tempo real
     */
    updateClock: function() {
        const clockElement = document.getElementById('current-time');
        if (!clockElement) return;

        const now = new Date();
        const timeString = now.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        clockElement.textContent = timeString;
    }
};

// Event Listeners Globais
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes da UI
    UI.init();
    
    // Atualizar relógio
    UI.updateClock();
    setInterval(UI.updateClock, 60000); // Atualizar a cada minuto
    
    // Event listeners para botões de cancelar reserva
    document.querySelectorAll('[onclick*="cancelReservation"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const reservationId = this.getAttribute('data-reservation-id') || 
                                 this.getAttribute('onclick').match(/\d+/)[0];
            
            Reservations.cancel(reservationId);
        });
    });
    
    // Smooth scroll para âncoras
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-hide alerts após 5 segundos
    setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
            if (alert.querySelector('.btn-close')) {
                alert.classList.add('fade');
                setTimeout(() => alert.remove(), 150);
            }
        });
    }, 5000);
    
    // Confirmação para ações destrutivas
    document.querySelectorAll('.btn-danger[type="submit"], .btn-danger[onclick]').forEach(button => {
        if (!button.hasAttribute('data-confirm-handled')) {
            button.addEventListener('click', function(e) {
                const action = this.textContent.trim().toLowerCase();
                let message = 'Tem certeza que deseja continuar?';
                
                if (action.includes('cancelar')) {
                    message = 'Tem certeza que deseja cancelar?';
                } else if (action.includes('excluir') || action.includes('deletar')) {
                    message = 'Tem certeza que deseja excluir? Esta ação não pode ser desfeita.';
                }
                
                if (!confirm(message)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
            button.setAttribute('data-confirm-handled', 'true');
        }
    });
});

// Sidebar responsivo
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar');
    const toggleButton = document.createElement('button');
    
    // Criar botão de toggle para mobile
    toggleButton.className = 'btn btn-primary d-md-none position-fixed';
    toggleButton.style.cssText = 'top: 20px; left: 20px; z-index: 1001;';
    toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
    
    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('show');
    });
    
    // Adicionar botão ao body se estiver em mobile
    if (window.innerWidth <= 768) {
        document.body.appendChild(toggleButton);
    }
    
    // Fechar sidebar ao clicar fora (mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(e.target) && 
            !toggleButton.contains(e.target) &&
            sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
    });
});

// Exportar para uso global
window.SalasTechUser = {
    Utils,
    Reservations,
    UI
};
