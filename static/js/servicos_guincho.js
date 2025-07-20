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

    const form = document.getElementById('servicoForm');
    const cadastrarBtn = document.getElementById('cadastrarBtn');
    const atualizarBtn = document.getElementById('atualizarBtn');
    const deletarBtn = document.getElementById('deletarBtn');

    form.addEventListener('submit', function(event) {
        // Lógica para cadastrar ou atualizar serviço de guincho
        form.submit();
    });

    document.addEventListener('DOMContentLoaded', substituirIdsPorNomesServicosGuincho);
    document.getElementById('pesquisa').addEventListener('keyup', filtrarSolicitacoes);
    document.getElementById('filtroDataInicio').addEventListener('change', filtrarSolicitacoes);
    document.getElementById('filtroDataFim').addEventListener('change', filtrarSolicitacoes);
    document.getElementById('filtroStatus').addEventListener('change', filtrarSolicitacoes);

    document.getElementById('atualizarBtn').addEventListener('click', atualizarServico);
    document.getElementById('deletarBtn').addEventListener('click', deletarServico);
});

function atualizarServico() {
    var form = document.getElementById('servicoForm');
    form.action = '/atualizar_servico_guincho';
    form.submit();
}

function deletarServico() {
    var form = document.getElementById('servicoForm');
    form.action = '/deletar_servico_guincho';
    form.submit();
}

function filtrarSolicitacoes() {
    var pesquisaInput = document.getElementById("pesquisa");
    var pesquisaFilter = pesquisaInput.value.toUpperCase();
    var filtroDataInicio = document.getElementById("filtroDataInicio").value;
    var filtroDataFim = document.getElementById("filtroDataFim").value;
    var filtroStatus = document.getElementById("filtroStatus").value;
  
    var table = document.getElementById("tabelaServicos");
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
                statusMatch = td[7].innerText.trim() === filtroStatus;
            }

            // Só exibe se passar em todos os filtros
            tr[i].style.display = (textMatch && dateMatch && statusMatch) ? "" : "none";
        }
    }
}

function projetarDadosServico(tr) {
    const tds = tr.getElementsByTagName("td");
    const servicoId = tds[0].textContent;

    // Carrega dados do serviço
    fetch(`/carregar_servico/${servicoId}`)
        .then(response => response.json())
        .then(servico => {
            document.getElementById('servico_id').value = servico.id;
            document.getElementById('data_solicitacao').value = servico.data_solicitacao;
            document.getElementById('guincho_id').value = servico.guincho_id;
            document.getElementById('tipo_solicitacao').value = servico.tipo_solicitacao;
            document.getElementById('protocolo').value = servico.protocolo;
            document.getElementById('origem').value = servico.origem;
            document.getElementById('destino').value = servico.destino;
            document.getElementById('status').value = servico.status;

            // Mostra botões de atualizar/deletar
            document.getElementById('cadastrarBtn').style.display = 'none';
            document.getElementById('atualizarBtn').style.display = 'inline';
            document.getElementById('deletarBtn').style.display = 'inline';
        });
}

// Substitui o ID do guincho pelo atributo desejado (como a placa) na tabela de serviços de guincho.
function substituirIdsPorNomesServicosGuincho() {
    const rows = document.querySelectorAll('#tabelaServicos tbody tr');
    rows.forEach(row => {
        // Na tabela de serviços, a coluna 2 (índice 2) contém o guincho_id.
        const guinchoId = row.cells[2].innerText.trim();
        if (guinchoId) {
            fetch(`/nome_guincho/${guinchoId}`)
                .then(response => response.json())
                .then(data => {
                    // Substitui o ID pelo valor descritivo (ex: a placa do guincho)
                    row.cells[2].innerText = data.placa;
                });
        }
    });
}
