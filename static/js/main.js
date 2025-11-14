// Funciones JavaScript adicionales para la plataforma CTF

// Función para formatear tiempo relativo
function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " años";
    
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " meses";
    
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " días";
    
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " horas";
    
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutos";
    
    return Math.floor(seconds) + " segundos";
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado al portapapeles!', 'success');
    }).catch(err => {
        console.error('Error al copiar:', err);
    });
}

// Función para mostrar toasts
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? 'var(--primary-color)' : 'var(--danger-color)'};
        color: var(--background);
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Función para validar formato de flag
function isValidFlag(flag) {
    return /^flag\{[a-zA-Z0-9_]+\}$/.test(flag);
}

// Función para animar números (contador)
function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

// Función para crear efecto de confetti
function createConfetti() {
    const colors = ['#00ff41', '#ff00ff', '#00ffff', '#ffff00', '#ff0000'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            top: -10px;
            left: ${Math.random() * 100}%;
            opacity: 1;
            z-index: 9999;
            pointer-events: none;
        `;
        
        document.body.appendChild(confetti);
        
        const animation = confetti.animate([
            { 
                transform: 'translateY(0) rotate(0deg)', 
                opacity: 1 
            },
            { 
                transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`, 
                opacity: 0 
            }
        ], {
            duration: 3000 + Math.random() * 2000,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        });
        
        animation.onfinish = () => confetti.remove();
    }
}

// Función para vibrar (si está disponible)
function vibrate(pattern = [100, 50, 100]) {
    if ('vibrate' in navigator) {
        navigator.vibrate(pattern);
    }
}

// Auto-actualizar timestamps
function updateTimestamps() {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach(element => {
        const date = element.getAttribute('data-timestamp');
        element.textContent = timeAgo(date) + ' ago';
    });
}

// Actualizar cada minuto
setInterval(updateTimestamps, 60000);

// Prevenir envío de formularios vacíos
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input[required]');
            let valid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = 'var(--danger-color)';
                } else {
                    input.style.borderColor = 'var(--primary-color)';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                showToast('Por favor completa todos los campos', 'error');
            }
        });
    });
});

// Detectar conexión perdida
window.addEventListener('offline', () => {
    showToast('Conexión perdida. Reconectando...', 'error');
});

window.addEventListener('online', () => {
    showToast('Conexión restaurada!', 'success');
});

// Exportar funciones globales
window.ctfUtils = {
    timeAgo,
    copyToClipboard,
    showToast,
    isValidFlag,
    animateNumber,
    createConfetti,
    vibrate,
    updateTimestamps
};
