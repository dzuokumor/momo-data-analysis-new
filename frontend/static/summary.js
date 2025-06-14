document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.metric-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const valueElement = this.querySelector('.metric-value');
            const subtextElement = this.querySelector('.metric-subtext');
            
            valueElement.innerHTML = '<div class="loading-spinner"></div>';
            if (subtextElement) subtextElement.textContent = '';
            
            const target = this.getAttribute('data-target');
            
            setTimeout(() => {
                loadCardData(target, valueElement, subtextElement);
            }, 2000);
        });
    });
});

function formatTransactionType(type) {
    const typeMap = {
        'deposit': 'Bank Deposit',
        'payment': 'Payment',
        'transfer': 'Money Transfer',
        'receive': 'Received Money',
        'bill_payment': 'Bill Payment'
    };
    return typeMap[type] || type;
}

async function loadCardData(target, valueElement, subtextElement) {
    try {
        let endpoint;
        switch(target) {
            case 'top-sender':
                endpoint = '/api/summary/top-senders';
                break;
            case 'top-recipient':
                endpoint = '/api/summary/top-recipients';
                break;
            case 'transaction-volume':
                endpoint = '/api/summary/hourly-activity';
                break;
            case 'busiest-hour':
                endpoint = '/api/summary/hourly-activity';
                break;
        }

        const response = await fetch(endpoint);
        const data = await response.json();

        if (target === 'top-sender' && data.length > 0) {
            valueElement.textContent = data[0].sender || 'No data';
            if (subtextElement) {
                subtextElement.textContent = `Sent ${formatCurrency(data[0].total_sent)}`;
            }
        }
        else if (target === 'top-recipient' && data.length > 0) {
            valueElement.textContent = data[0].recipient || 'No data';
            if (subtextElement) {
                subtextElement.textContent = `${data[0].transaction_count} transactions`;
            }
        }
        else if (target === 'transaction-volume') {
            const totalVolume = data.reduce((sum, hour) => sum + hour.total_amount, 0);
            valueElement.textContent = formatCurrency(totalVolume);
        }
        else if (target === 'busiest-hour' && data.length > 0) {
            const busiestHour = data.reduce((prev, current) => 
                (prev.transaction_count > current.transaction_count) ? prev : current
            );
            valueElement.textContent = `${busiestHour.hour}:00`;
        }

    } catch (error) {
        console.error(`Error loading ${target} data:`, error);
        valueElement.textContent = 'Error';
        if (subtextElement) subtextElement.textContent = '';
    }
}


async function loadCharts() {
    try {
        console.log("Fetching chart data...");
        const [senders, recipients, types] = await Promise.all([
            fetch('/api/summary/top-senders').then(res => res.json()),
            fetch('/api/summary/top-recipients').then(res => res.json()),
            fetch('/api/transaction-types').then(res => res.json())
        ]);

        console.log("Chart data received:", {senders, recipients, types});

        setTimeout(() => {
            if (senders?.length > 0) {
                console.log("Creating senders chart with data:", senders);
                createTopSendersChart(senders);
            } else {
                console.warn("No senders data available");
            }
            
            if (recipients?.length > 0) {
                console.log("Creating recipients chart with data:", recipients);
                createTopRecipientsChart(recipients);
            } else {
                console.warn("No recipients data available");
            }
            
            if (types?.length > 0) {
                console.log("Creating types chart with data:", types);
                createTransactionTypesChart(types);
            } else {
                console.warn("No transaction types data available");
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error loading chart data:', error);
        document.querySelectorAll('.chart-container').forEach(container => {
            container.innerHTML += '<p class="chart-error">Failed to load chart data</p>';
        });
    }
}

function createTopSendersChart(data) {
    const ctx = document.getElementById('topSendersChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.sender || 'Unknown'),
            datasets: [{
                label: 'Amount Sent (RWF)',
                data: data.map(item => item.total_sent),
                backgroundColor: '#4f46e5',
                borderColor: '#4f46e5',
                borderWidth: 1,
                barPercentage: 0.8 
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value, true);
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    title: {
                        display: true,
                        text: 'Amount (RWF)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                y: {
                    ticks: {
                        font: {
                            size: 12
                        },
                        autoSkip: false
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            }
        }
    });
}

function createTopRecipientsChart(data) {
    const ctx = document.getElementById('topRecipientsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.recipient),
            datasets: [{
                label: 'Transaction Count',
                data: data.map(item => item.transaction_count),
                backgroundColor: '#10b981',
                borderColor: '#10b981',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function createTransactionTypesChart(data) {
    const chartData = data
        .filter(item => item.total_amount > 0)
        .map(item => ({
            ...item,
            formattedType: formatTransactionType(item.type),
            formattedAmount: formatCurrency(item.total_amount)
        }));

    console.log("Formatted chart data:", chartData);

    const ctx = document.getElementById('transactionTypesChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.map(item => `${item.formattedType} (${item.formattedAmount})`),
            datasets: [{
                data: chartData.map(item => item.total_amount),
                backgroundColor: [
                    '#4f46e5', 
                    '#10b981', 
                    '#f59e0b', 
                    '#ef4444', 
                    '#8b5cf6'  
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label.split(' (')[0]}: ${percentage}% (${formatCurrency(value)})`;
                        }
                    }
                }
            }
        }
    });
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.metric-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
        });
    });
    
    loadCharts();
});

function formatCurrency(amount) {
    return 'RWF ' + (amount || 0).toLocaleString('en-RW');
}