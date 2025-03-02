function filtrarAnexos() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("pesquisa");
    filter = input.value.toUpperCase();
    table = document.getElementById("tabelaAnexos");
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

function projetarDadosAnexo(anexo) {
    document.getElementById('anexo_id').value = anexo[0];
    document.getElementById('transacao_id').value = anexo[1];
    document.getElementById('tipo').value = anexo[3];

    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function atualizarAnexo() {
    var form = document.getElementById('anexoForm');
    form.action = '/atualizar_anexo';
    form.submit();
}

function deletarAnexo() {
    var form = document.getElementById('anexoForm');
    form.action = '/deletar_anexo';
    form.submit();
}
