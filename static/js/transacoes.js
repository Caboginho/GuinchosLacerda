document.addEventListener('DOMContentLoaded', function() {
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    }

    const form = document.getElementById('transacaoForm');
    const cadastrarBtn = document.getElementById('cadastrarBtn');
    const atualizarBtn = document.getElementById('atualizarBtn');
    const deletarBtn = document.getElementById('deletarBtn');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);  // Mostra mensagem de sucesso
                // Redireciona para página de transações
                if (window.location.pathname.includes('/admin')) {
                    window.location.href = '/admin/transacoes_pg';
                } else {
                    window.location.href = '/sec/transacoes_pg';
                }
            } else {
                alert(data.error || 'Erro ao cadastrar transação');
            }
        })
        .catch(error => {
            alert('Erro ao processar requisição: ' + error);
        });
    });

    document.getElementById('pesquisa').addEventListener('keyup', filtrarTransacoes);
    document.getElementById('filtroDataInicio').addEventListener('change', filtrarTransacoes);
    document.getElementById('filtroDataFim').addEventListener('change', filtrarTransacoes);
    document.getElementById('filtroStatus').addEventListener('change', filtrarTransacoes);
    document.getElementById('atualizarBtn').addEventListener('click', atualizarTransacao);
    document.getElementById('deletarBtn').addEventListener('click', deletarTransacao);
});

function filtrarTransacoes() {
    var pesquisaInput = document.getElementById("pesquisa");
    var pesquisaFilter = pesquisaInput.value.toUpperCase();
    var filtroDataInicio = document.getElementById("filtroDataInicio").value;
    var filtroDataFim = document.getElementById("filtroDataFim").value;
    var filtroStatus = document.getElementById("filtroStatus").value;
  
    var table = document.getElementById("tabelaTransacoes");
    var tr = table.getElementsByTagName("tr");
  
    // Percorre as linhas, pulando o cabeçalho (índice 0)
    for (var i = 1; i < tr.length; i++) {
        var td = tr[i].getElementsByTagName("td");
        if (td.length > 0) {
            // Verifica o filtro de texto
            var txtValue = "";
            for (var j = 0; j < td.length; j++) {
                txtValue += td[j].textContent || td[j].innerText;
            }
            var textMatch = txtValue.toUpperCase().indexOf(pesquisaFilter) > -1;

            // Verifica o filtro de data
            var dateCell = new Date(td[1].innerText);
            var dateMatch = true;
            
            if (filtroDataInicio) {
                var dataInicio = new Date(filtroDataInicio);
                if (dateCell < dataInicio) dateMatch = false;
            }
            if (filtroDataFim) {
                var dataFim = new Date(filtroDataFim);
                if (dateCell > dataFim) dateMatch = false;
            }

            // Verifica o filtro de status
            var statusMatch = true;
            if (filtroStatus !== "") {
                statusMatch = td[6].innerText.trim() === filtroStatus;
            }

            // Só exibe se passar em todos os filtros
            tr[i].style.display = (textMatch && dateMatch && statusMatch) ? "" : "none";
        }
    }
}

function projetarDadosTransacao(row) {
    var cells = row.getElementsByTagName("td");
    document.getElementById("transacao_id").value = cells[0].innerText;
    document.getElementById("data").value = cells[1].innerText;
    document.getElementById("valor").value = cells[2].innerText;
    document.getElementById("categoria").value = cells[3].innerText;
    document.getElementById("descricao").value = cells[4].innerText;
    document.getElementById("metodo_pagamento").value = cells[5].innerText;
    document.getElementById("status").value = cells[6].innerText;

    document.getElementById("cadastrarBtn").style.display = "none";
    document.getElementById("atualizarBtn").style.display = "inline-block";
    document.getElementById("deletarBtn").style.display = "inline-block";

    // Desabilita campo de anexos para manter os existentes
    document.getElementById('anexos').disabled = true;

    // Busca e exibe anexos existentes
    fetch(`/buscar_anexos_transacao/${cells[0].innerText}`)
        .then(response => response.json())
        .then(data => {
            const anexosDiv = document.getElementById('anexosDiv');
            const anexosContainer = document.getElementById('anexosContainer');
            anexosContainer.innerHTML = '';
            
            if (data.anexos && data.anexos.length > 0) {
                data.anexos.forEach(anexo => {
                    const anexoElement = document.createElement('div');
                    anexoElement.className = 'anexo-item';
                    anexoElement.innerHTML = `
                        <a href="${anexo.url}" target="_blank" download>
                            ${anexo.referencia} (Clique para baixar)
                        </a>`;
                    anexosContainer.appendChild(anexoElement);
                });
                anexosDiv.style.display = 'block';
            }
        });
}

function mostrarAnexos(transacaoId) {
    fetch(`/anexos_transacao/${transacaoId}`)
        .then(response => response.json())
        .then(data => {
            const anexosDiv = document.getElementById('anexosDiv');
            const anexosContainer = document.getElementById('anexosContainer');
            anexosContainer.innerHTML = '';
            data.anexos.forEach(anexo => {
                const anexoElement = document.createElement('div');
                const link = document.createElement('a');
                link.href = anexo.url;
                link.target = '_blank';
                link.textContent = anexo.url.split('/').pop();
                anexoElement.appendChild(link);
                anexosContainer.appendChild(anexoElement);
            });
            anexosDiv.style.display = 'block';
        });
}

function atualizarTransacao() {
    document.getElementById('transacaoForm').action = '/atualizar_transacao';
    document.getElementById('transacaoForm').submit();
}

function deletarTransacao() {
    document.getElementById('transacaoForm').action = '/deletar_transacao';
    document.getElementById('transacaoForm').submit();
}

function substituirIdsPorNomesTransacoes() {
    const rows = document.querySelectorAll('#tabelaTransacoes tbody tr');
    rows.forEach(row => {
        const secretariaId = row.cells[6].innerText.trim();
        if (secretariaId) {
            fetch(`/nome_secretaria/${secretariaId}`)
                .then(response => response.json())
                .then(data => {
                    row.cells[6].innerText = data.nome;
                });
        }
        const guinchoId = row.cells[7] ? row.cells[7].innerText.trim() : "";
        if (guinchoId) {
            fetch(`/nome_guincho/${guinchoId}`)
                .then(response => response.json())
                .then(data => {
                    row.cells[7].innerText = data.placa;
                });
        }
        const motoristaId = row.cells[8] ? row.cells[8].innerText.trim() : "";
        if (motoristaId) {
            fetch(`/nome_motorista/${motoristaId}`)
                .then(response => response.json())
                .then(data => {
                    row.cells[8].innerText = data.nome;
                });
        }
    });
}

document.addEventListener('DOMContentLoaded', substituirIdsPorNomesTransacoes);

// Adiciona listener para carregar dados quando uma secretaria é selecionada
document.addEventListener('DOMContentLoaded', function() {
    const secretariaSelect = document.getElementById('secretaria_id');
    if (secretariaSelect) {
        // Carrega dados da primeira secretaria da lista se houver
        if (secretariaSelect.options.length > 1) {
            secretariaSelect.selectedIndex = 1; // Primeira secretaria após o placeholder
            atualizarTabelaPorSecretaria(secretariaSelect.value);
        }

        secretariaSelect.addEventListener('change', function() {
            if (this.value) {
                // Primeiro limpa as tabelas locais
                fetch('/admin/limpar_dados_locais', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(() => {
                    // Depois carrega dados da secretaria selecionada
                    window.location.href = `/transacoes_pg?secretaria_id=${this.value}`;
                });
            }
        });
    }
});

function atualizarTabelaPorSecretaria(secretariaId) {
    if (!secretariaId) return;
    
    // Primeiro atualiza o banco local com dados da secretaria selecionada
    fetch(`/admin/carregar_dados_secretaria/${secretariaId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Depois busca as transações atualizadas
            return fetch(`/admin/transacoes/por_secretaria/${secretariaId}`);
        }
        throw new Error('Falha ao carregar dados da secretaria');
    })
    .then(response => response.json())
    .then(data => {
        const tbody = document.querySelector('#tabelaTransacoes tbody');
        tbody.innerHTML = '';

        if (data.transacoes && data.transacoes.length > 0) {
            data.transacoes.forEach(transacao => {
                const tr = document.createElement('tr');
                tr.onclick = () => projetarDadosTransacao(tr);
                tr.innerHTML = `
                    <td>${transacao.id}</td>
                    <td>${transacao.data}</td>
                    <td>${transacao.valor}</td>
                    <td>${transacao.categoria}</td>
                    <td>${transacao.descricao}</td>
                    <td>${transacao.metodo_pagamento}</td>
                    <td>${transacao.status}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7">Nenhuma transação disponível</td></tr>';
        }
    })
    .catch(error => console.error('Erro:', error));
}
