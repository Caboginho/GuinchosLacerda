function loadContent(route) {
    const iframe = document.getElementById('content');
    // Adiciona /admin antes de cada rota
    iframe.src = '/admin' + route;
    iframe.onload = function() {
        resizeIframe(this);
    };
}

function resizeIframe(iframe) {
    try {
        iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';

        if (window.innerWidth > 700) {
            iframe.style.width = '80%';
        } else {
            iframe.style.width = '90%';
        }
    } catch (e) {
        console.error('Erro ao redimensionar iframe:', e);
    }
}

function logout() {
    window.location.href = '/logout';
}

// Carrega a página de usuários por padrão quando a página admin carrega
document.addEventListener('DOMContentLoaded', function() {
    loadContent('/usuarios');
});
