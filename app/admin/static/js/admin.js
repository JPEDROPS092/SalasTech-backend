/**
 * SalasTech Admin - Funções comuns do painel administrativo
 */

// Função para confirmar exclusão
function confirmDelete(roomId, roomName) {
    // Atualizar o modal com os dados da sala
    document.getElementById('roomName').textContent = roomName;
    document.getElementById('deleteForm').action = '/admin/rooms/' + roomId + '/delete';
    
    // Abrir o modal
    var deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    deleteModal.show();
}

// Inicializar toasts
document.addEventListener('DOMContentLoaded', function() {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
    });
});
