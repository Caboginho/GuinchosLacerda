function filtrarSolicitacoes() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("pesquisa");
    filter = input.value.toUpperCase();
    table = document.getElementById("tabelaServicos");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        if (td) {
            txtValue = "";
            for (var j = 0; j < td.length; j++) {
                txtValue += td[j].textContent || td[j].innerText;
            }
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function projetarDadosServico(servico) {
    document.getElementById('servico_id').value = servico[0];
    document.getElementById('data_solicitacao').value = servico[1];
    document.getElementById('guincho_id').value = servico[2];
    document.getElementById('tipo_solicitacao').value = servico[3];
    document.getElementById('protocolo').value = servico[4];
    document.getElementById('origem').value = servico[5];
    document.getElementById('destino').value = servico[6];
    document.getElementById('status').value = servico[7];

    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

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
