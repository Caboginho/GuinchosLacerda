function filtrarUsuarios() {
    const input = document.getElementById('pesquisa');
    const filtro = input.value.toUpperCase();
    const tabela = document.getElementById('tabelaUsuarios');
    const linhas = tabela.getElementsByTagName('tr');

    for (let i = 1; i < linhas.length; i++) {
        const colunas = linhas[i].getElementsByTagName('td');
        let exibir = false;
        for (let j = 0; j < colunas.length; j++) {
            if (colunas[j].innerText.toUpperCase().indexOf(filtro) > -1) {
                exibir = true;
                break;
            }
        }
        linhas[i].style.display = exibir ? '' : 'none';
    }
}

function projetarDadosUsuario(linha) {
    const colunas = linha.getElementsByTagName('td');
    document.getElementById('usuario_id').value = colunas[0].innerText;
    document.getElementById('nome').value = colunas[1].innerText;
    document.getElementById('email').value = colunas[2].innerText;
    document.getElementById('senha').value = ''; // Não exibir a senha
    document.getElementById('tipo').value = colunas[3].innerText;
    document.getElementById('cnh').value = colunas[4].innerText;
    document.getElementById('celular').value = colunas[5].innerText;
    document.getElementById('justificativa').value = colunas[6].innerText;

    document.getElementById('cadastrarBtn').style.display = 'none';
    document.getElementById('atualizarBtn').style.display = 'inline';
    document.getElementById('deletarBtn').style.display = 'inline';
}

function atualizarUsuario() {
    document.getElementById('usuarioForm').action = '/atualizar_usuario';
    document.getElementById('usuarioForm').submit();
}

function deletarUsuario() {
    document.getElementById('usuarioForm').action = '/deletar_usuario';
    document.getElementById('usuarioForm').submit();
}

function toggleSenhaObrigatoria() {
    const tipo = document.getElementById('tipo').value;
    const senha = document.getElementById('senha');
    if (tipo === 'Motorista') {
        senha.removeAttribute('required');
    } else {
        senha.setAttribute('required', 'required');
    }
}
