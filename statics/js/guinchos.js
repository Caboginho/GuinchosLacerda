function filtrarGuinchos() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("pesquisa");
    filter = input.value.toUpperCase();
    table = document.getElementById("tabelaGuinchos");
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

function projetarDadosGuincho(tr) {
    var tds = tr.getElementsByTagName("td");
    document.getElementById('guincho_id').value = tds[0].textContent;
    document.getElementById('placa').value = tds[1].textContent;
    document.getElementById('modelo').value = tds[2].textContent;
    document.getElementById('motorista_id').value = tds[3].textContent;
    document.getElementById('secretaria_id').value = tds[4].textContent;
    document.getElementById('disponivel').value = tds[5].textContent;

    document.getElementById('cadastrarBtn').disabled = true;
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function atualizarGuincho() {
    var form = document.getElementById('guinchoForm');
    form.action = '/atualizar_guincho';
    form.submit();
}

function deletarGuincho() {
    var form = document.getElementById('guinchoForm');
    form.action = '/deletar_guincho';
    form.submit();
}

document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('guinchosTable');
    const cadastrarButton = document.getElementById('cadastrarBtn');

    table.addEventListener('click', function(event) {
        const target = event.target;
        if (target.tagName === 'TD') {
            cadastrarButton.style.display = 'none';
        }
    });
});
