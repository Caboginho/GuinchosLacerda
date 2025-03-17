// index.js

// Função para carregar conteúdo parcial via fetch e injetá-lo na div com id "conteudo"
function carregarConteudo(url) {
    const conteudoDiv = document.getElementById("conteudo");
    // Exibe uma mensagem de carregamento
    conteudoDiv.innerHTML = "<p>Carregando...</p>";
  
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error("Erro ao carregar: " + response.statusText);
        }
        return response.text();
      })
      .then(data => {
        conteudoDiv.innerHTML = data;
        // Caso seja necessário, aqui você pode reinicializar scripts específicos
        // Por exemplo, se os partials usam collapsible, você pode reexecutar a lógica.
      })
      .catch(error => {
        console.error("Erro ao carregar conteúdo:", error);
        conteudoDiv.innerHTML = "<p>Erro ao carregar conteúdo. Tente novamente.</p>";
      });
  }
  
  // Expondo a função globalmente para que os botões do menu possam utilizá-la
  window.carregarConteudo = carregarConteudo;
  
  // Ao carregar a página, opcionalmente carrega um conteúdo padrão (ex: Usuários)
  document.addEventListener("DOMContentLoaded", function() {
    carregarConteudo("/usuarios_pg");
  });
  