document.addEventListener('DOMContentLoaded', () => {
    const dashboardLink = document.getElementById('dashboard-link');
    const summaryLink = document.getElementById('summary-link');
    const exitLink = document.getElementById('exit-link');
    const dashboardSection = document.getElementById('dashboard');
    const summarySection = document.getElementById('summary');
    const moneyFlowChartCanvas = document.getElementById('moneyFlowChart');
    const transactionTypeChartCanvas = document.getElementById('transactionTypeChart');
    const highestSenderCard = document.getElementById('highestSenderCard');
    const totalVolumeCard = document.getElementById('totalVolumeCard');
    const averageTransactionCard = document.getElementById('averageTransactionCard');

    let moneyFlowChart, transactionTypeChart;

    function showSection(section) {
        // Remove 'active' class from ALL sections
        dashboardSection.classList.remove('active');
        summarySection.classList.remove('active');

        // Add 'active' class to the selected section
        section.classList.add('active');
    }

    dashboardLink.addEventListener('click', () => showSection(dashboardSection));
    summaryLink.addEventListener('click', () => showSection(summarySection));
    exitLink.addEventListener('click', () => {
        window.location.href = "https://www.google.com";
    });

    // Show the dashboard section by default on page load.
    showSection(dashboardSection); // This line is crucial

    Promise.all([
        fetch('/api/money-flow').then(r => r.json()),
        fetch('/api/transaction-types').then(r => r.json()),
        fetch('/api/highest-sender').then(r => r.json()),
        fetch('/api/total-transaction-volume').then(r => r.json()),
        fetch('/api/average-transaction-size').then(r => r.json())
    ])
    .then(([moneyFlowData, transactionTypeData, highestSenderData, totalVolumeData, averageTransactionData]) => {
        createMoneyFlowChart(moneyFlowChartCanvas, moneyFlowData);
        createTransactionTypeChart(transactionTypeChartCanvas, transactionTypeData);

        highestSenderCard.textContent = highestSenderData && highestSenderData.length > 0
            ? `Highest Sender: ${highestSenderData[0].sender} (${highestSenderData[0].total_sent} RWF)`
            : "No sender data available";

        totalVolumeCard.textContent = totalVolumeData && totalVolumeData.length > 0
            ? `Total Volume: ${totalVolumeData[0].total_volume} RWF`
            : "No volume data available";

        averageTransactionCard.textContent = averageTransactionData && averageTransactionData.length > 0
            ? `Average Transaction: ${averageTransactionData[0].average_size} RWF`
            : "No average transaction data available";
    })
    .catch(error => console.error("Error fetching data:", error));

    function createMoneyFlowChart(canvas, data) {
        if (!data || data.length === 0) return;
        const ctx = canvas.getContext('2d');
        moneyFlowChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Money In', 'Money Out'],
                datasets: [{
                    label: 'Amount (RWF)',
                    data: [data[0].money_in || 0, data[0].money_out || 0],
                    backgroundColor: ['green', 'red'],
                    borderColor: ['green', 'red'],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function createTransactionTypeChart(canvas, data) {
        if (!data || data.length === 0) return;
        const ctx = canvas.getContext('2d');
        const labels = ['Sent', 'Received', 'Airtime', 'Bills', 'Deposits'];
        const dataValues = labels.map(label => data[0][label.toLowerCase()] || 0);

        transactionTypeChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Amount (RWF)',
                    data: dataValues,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
        });
    }
});