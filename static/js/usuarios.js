// Inicialização quando o DOM carrega
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('usuarioForm');
    
    // Handler único para o formulário
    form.addEventListener('submit', handleFormSubmit);

    // Handlers para os botões
    const deletarBtn = document.getElementById('deletarBtn');
    if (deletarBtn) {
        deletarBtn.addEventListener('click', handleDelete);
    }

    // Handler para o botão atualizar
    const atualizarBtn = document.getElementById('atualizarBtn');
    if (atualizarBtn) {
        atualizarBtn.addEventListener('click', function() {
            const userId = document.getElementById('usuario_id').value;
            if (!userId) {
                alert('Selecione um usuário para atualizar');
                return;
            }
            
            const formData = new FormData(form);
            formData.set('usuario_id', userId); // Garante que o ID está presente
            
            submitRequest('/admin/usuarios/atualizar', formData);
        });
    }

    // Event listeners essenciais
    document.getElementById('novoBtn').addEventListener('click', limparFormulario);
    document.getElementById('pesquisa').addEventListener('keyup', filtrarUsuarios);
    document.getElementById('tipo').addEventListener('change', toggleSenhaObrigatoria);
});

// Funções CRUD principais
function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const userId = document.getElementById('usuario_id').value;
    
    const url = userId ? '/admin/usuarios/atualizar' : '/admin/usuarios/cadastrar';
    if (userId) {
        formData.set('usuario_id', userId);
    }
    
    submitRequest(url, formData);
}

function handleDelete() {
    const userId = document.getElementById('usuario_id').value;
    
    if (!userId || !confirm('Confirma a exclusão deste usuário?')) {
        return;
    }
    
    submitRequest(`/admin/usuarios/deletar/${userId}`, null, 'POST');
}

// Função de submissão de requisições
function submitRequest(url, formData = null, method = 'POST') {
    const options = {
        method: method,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    if (formData) {
        options.body = formData;
    }
    
    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return response.json();
        })
        .then(data => {
            alert(data.error || data.message);
            if (!data.error) {
                window.location.href = '/admin/usuarios';
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao processar requisição');
        });
}

// Funções auxiliares essenciais
function projetarDadosUsuario(tr) {
    // Remove seleção anterior
    document.querySelectorAll('#tabelaUsuarios tr').forEach(row => 
        row.classList.remove('selected')
    );
    tr.classList.add('selected');

    // Preenche formulário com dados da linha selecionada
    const tds = tr.getElementsByTagName('td');
    const userId = parseInt(tds[0].textContent);
    
    // Garante que o ID é um número válido
    if (isNaN(userId)) {
        console.error('ID inválido na tabela');
        return;
    }
    
    document.getElementById('usuario_id').value = userId;
    document.getElementById('nome').value = tds[1].textContent.trim();
    document.getElementById('email').value = tds[2].textContent.trim();
    document.getElementById('tipo').value = tds[3].textContent.trim();
    document.getElementById('cnh').value = tds[4].textContent.trim();
    document.getElementById('celular').value = tds[5].textContent.trim();
    document.getElementById('justificativa').value = tds[6].textContent.trim();

    // Limpa senha e ajusta required
    document.getElementById('senha').value = '';
    document.getElementById('senha').required = false;

    // Ajusta visibilidade dos botões
    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function limparFormulario() {
    const form = document.getElementById('usuarioForm');
    form.reset();
    
    document.getElementById('usuario_id').value = '';
    document.getElementById('senha').required = true;
    
    document.getElementById('cadastrarBtn').style.display = 'inline';
    document.getElementById('atualizarBtn').style.display = 'none';
    document.getElementById('deletarBtn').style.display = 'none';
    
    document.querySelectorAll('#tabelaUsuarios tr').forEach(row => 
        row.classList.remove('selected')
    );
}

function filtrarUsuarios() {
    const filtro = document.getElementById('pesquisa').value.toLowerCase();
    const linhas = document.querySelectorAll('#tabelaUsuarios tbody tr');
    
    linhas.forEach(linha => {
        const texto = linha.textContent.toLowerCase();
        linha.style.display = texto.includes(filtro) ? '' : 'none';
    });
}

function toggleSenhaObrigatoria() {
    const tipo = document.getElementById('tipo').value;
    const senha = document.getElementById('senha');
    senha.required = tipo !== 'Motorista';
}
