document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('guinchoForm');
    form.addEventListener('submit', handleFormSubmit);
    document.getElementById('deletarBtn').addEventListener('click', handleDelete);
    document.getElementById('pesquisa').addEventListener('keyup', filtrarGuinchos);
});

function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const guinchoId = document.getElementById('guincho_id').value;
    
    const url = guinchoId 
        ? '/admin/guinchos/atualizar' 
        : '/admin/guinchos/cadastrar';
        
    submitRequest(url, formData);
}

function handleDelete() {
    const guinchoId = document.getElementById('guincho_id').value;
    if (!guinchoId || !confirm('Confirma a exclusão deste guincho?')) {
        return;
    }
    submitRequest(`/admin/guinchos/deletar/${guinchoId}`, null);
}

function projetarDadosGuincho(tr) {
    document.querySelectorAll('#tabelaGuinchos tr').forEach(row => 
        row.classList.remove('selected')
    );
    tr.classList.add('selected');

    const tds = tr.getElementsByTagName('td');
    document.getElementById('guincho_id').value = tds[0].textContent;
    document.getElementById('modelo').value = tds[1].textContent.trim();
    document.getElementById('placa').value = tds[2].textContent.trim();
    document.getElementById('secretaria_id').value = tds[3].getAttribute('data-id') || '';
    document.getElementById('motorista_id').value = tds[4].getAttribute('data-id') || '';
    document.getElementById('status').value = tds[5].textContent.trim();

    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function filtrarGuinchos() {
    const termo = document.getElementById('pesquisa').value.toLowerCase();
    document.querySelectorAll('#tabelaGuinchos tbody tr').forEach(linha => {
        linha.style.display = 
            linha.textContent.toLowerCase().includes(termo) ? '' : 'none';
    });
}

function submitRequest(url, formData) {
    const options = {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    };
    
    if (formData) {
        options.body = formData;
    }

    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Erro no servidor');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            alert(data.message || 'Operação realizada com sucesso');
            window.location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
            alert(error.message || 'Erro ao processar requisição');
        });
}
