document.addEventListener('DOMContentLoaded', function() {
    loadCharts();

    const filtrarBtn = document.getElementById('filtrarBtn');
    filtrarBtn.addEventListener('click', function() {
        loadCharts();
    });

    const dados = JSON.parse(document.getElementById('dadosFinanceiros').textContent);
    initGraficos(dados);
    atualizarTotais(dados);
});

let barChartInstance = null;
let pieChartInstance = null;

function loadCharts() {
    const dataInicio = document.getElementById('data_inicio').value;
    const dataFim = document.getElementById('data_fim').value;

    let url = '/financeiro/dados';
    if (dataInicio || dataFim) {
        url += `?data_inicio=${dataInicio}&data_fim=${dataFim}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateBarChart(data.barChart);
            updatePieChart(data.pieChart);
        })
        .catch(error => console.error("Erro ao carregar os gráficos:", error));
}

function updateBarChart(barData) {
    const ctx = document.getElementById('barChart').getContext('2d');

    if (barChartInstance) {
        barChartInstance.destroy();
    }

    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: barData.labels,
            datasets: barData.datasets.map(ds => ({
                label: ds.label,
                data: ds.data,
                backgroundColor: getRandomColor(),
                borderColor: getRandomColor(),
                borderWidth: 1
            }))
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updatePieChart(pieData) {
    const ctx = document.getElementById('pieChart').getContext('2d');

    if (pieChartInstance) {
        pieChartInstance.destroy();
    }

    pieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: pieData.labels,
            datasets: [{
                data: pieData.data,
                backgroundColor: pieData.labels.map(() => getRandomColor())
            }]
        },
        options: {
            responsive: true,
        }
    });
}

function getRandomColor() {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    return `rgba(${r}, ${g}, ${b}, 0.7)`;
}

function initGraficos(dados) {
    // Gráfico de Receitas Mensais
    const ctxReceitas = document.getElementById('graficoReceitas').getContext('2d');
    new Chart(ctxReceitas, {
        type: 'line',
        data: {
            labels: dados.grafico_mensal.map(item => item.mes),
            datasets: [{
                label: 'Receitas Mensais',
                data: dados.grafico_mensal.map(item => item.valor),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `R$ ${value.toFixed(2)}`
                    }
                }
            }
        }
    });

    // Gráfico de Tipos de Serviço
    const ctxServicos = document.getElementById('graficoServicos').getContext('2d');
    new Chart(ctxServicos, {
        type: 'pie',
        data: {
            labels: dados.grafico_tipos.labels,
            datasets: [{
                data: dados.grafico_tipos.data,
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Atualiza cards com totais
function atualizarTotais(dados) {
    document.getElementById('totalReceitas').textContent = 
        `R$ ${dados.total_receitas.toFixed(2)}`;
    document.getElementById('totalServicos').textContent = 
        dados.total_servicos;
}
