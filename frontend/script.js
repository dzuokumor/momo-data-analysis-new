// Monthly Expenses Chart (Bar Chart)
const expensesCtx = document.getElementById('expensesChart').getContext('2d');
new Chart(expensesCtx, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'], // X-axis labels (months)
        datasets: [{
            label: 'Money Out', // Legend label
            data: [400, 300, 200, 350, 400], // Y-axis data for Money Out
            backgroundColor: '#dc3545', // Red color for Money Out
            borderWidth: 0
        }, {
            label: 'Money In', // Legend label
            data: [200, 350, 150, 300, 250], // Y-axis data for Money In
            backgroundColor: '#198754', // Green color for Money In
            borderWidth: 0
        }]
    },
    options: {
        plugins: {
            legend: {
                display: true,
                position: 'top' // Legend position
            }
        },
        scales: {
            y: {
                beginAtZero: true, // Y-axis starts at 0
                max: 500, // Maximum value on Y-axis
                ticks: {
                    stepSize: 100 // Interval between ticks
                }
            }
        }
    }
});

// Expense Distribution Chart (Doughnut Chart)
const distributionCtx = document.getElementById('distributionChart').getContext('2d');
new Chart(distributionCtx, {
    type: 'doughnut',
    data: {
        labels: [
            'Send Money (Out)',
            'Received (In)',
            'Airtime (Out)',
            'Bills (Out)',
            'Deposits (In)'
        ],
        datasets: [{
            data: [30, 35, 15, 10, 10], // Data values for each category
            backgroundColor: [
                '#ff6384', // Red for Send Money (Out)
                '#36a2eb', // Blue for Received (In)
                '#ffcd56', // Yellow for Airtime (Out)
                '#4bc0c0', // Teal for Bills (Out)
                '#9966ff'  // Purple for Deposits (In)
            ],
            borderWidth: 0 // No border
        }]
    },
    options: {
        plugins: {
            legend: {
                position: 'right' // Legend position
            }
        },
        cutout: '60%' // Size of the inner hole in the doughnut chart
    }
});