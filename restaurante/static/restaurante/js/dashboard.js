document.addEventListener('DOMContentLoaded', () => {
    const elMes = document.getElementById('dados-mes');
    const canvasMes = document.getElementById('grafico-mes');
    if (elMes && canvasMes && typeof Chart !== 'undefined') {
        const dadosMes = JSON.parse(elMes.textContent);
        new Chart(canvasMes, {
            type: 'bar',
            data: {
                labels: dadosMes.map(d => d.mes),
                datasets: [{
                    label: 'Comandas por mês',
                    data: dadosMes.map(d => d.total),
                    backgroundColor: '#5c1d16',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    const elStatus = document.getElementById('dados-status');
    const canvasStatus = document.getElementById('grafico-status');
    if (elStatus && canvasStatus && typeof Chart !== 'undefined') {
        const dadosStatus = JSON.parse(elStatus.textContent);
        new Chart(canvasStatus, {
            type: 'doughnut',
            data: {
                labels: dadosStatus.map(d => d.status),
                datasets: [{
                    data: dadosStatus.map(d => d.total),
                    backgroundColor: ['#2d6a4f', '#5c1d16', '#d97706']
                }]
            },
            options: {
                responsive: true
            }
        });
    }
});
