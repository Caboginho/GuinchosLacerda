function atualizarGuinchos() {
    const secretariaId = document.getElementById('secretaria_id').value;
    fetch(`/guinchos_secretaria/${secretariaId}`)
        .then(response => response.json())
        .then(data => {
            const guinchoSelect = document.getElementById('guincho_id');
            guinchoSelect.innerHTML = '';
            data.guinchos.forEach(guincho => {
                const option = document.createElement('option');
                option.value = guincho.id;
                option.textContent = guincho.placa;
                guinchoSelect.appendChild(option);
            });
        });
}

function atualizarMotorista() {
    const guinchoId = document.getElementById('guincho_id').value;
    fetch(`/motorista_guincho/${guinchoId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('motorista_id').value = data.motorista;
        });
}

function filtrarTransacoes() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("pesquisa");
    filter = input.value.toUpperCase();
    table = document.getElementById("tabelaTransacoes");
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

function projetarDadosTransacao(transacao) {
    document.getElementById('transacao_id').value = transacao[0];
    document.getElementById('data').value = transacao[1];
    document.getElementById('valor').value = transacao[2];
    document.getElementById('categoria').value = transacao[3];
    document.getElementById('descricao').value = transacao[4];
    document.getElementById('metodo_pagamento').value = transacao[5];
    document.getElementById('status').value = transacao[10];

    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function atualizarTransacao() {
    var form = document.getElementById('transacaoForm');
    form.action = '/atualizar_transacao';
    form.submit();
}

function deletarTransacao() {
    var form = document.getElementById('transacaoForm');
    form.action = '/deletar_transacao';
    form.submit();
}

document.getElementById('tabelaTransacoes').addEventListener('click', function(e) {
    if (e.target && e.target.nodeName == "TD") {
        var tr = e.target.parentNode;
        var tds = tr.getElementsByTagName("td");
        document.getElementById('campo1').value = tds[0].textContent;
        document.getElementById('campo2').value = tds[1].textContent;
        document.getElementById('campo3').value = tds[2].textContent;
        document.getElementById('campo4').value = tds[3].textContent;
        document.getElementById('campo5').value = tds[4].textContent;
    }
});
