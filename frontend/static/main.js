function formatCurrency(amount) {
    return 'RWF ' + (amount || 0).toLocaleString('en-RW');
}

function formatTransactionType(type) {
    const types = {
        'receive': 'Received',
        'deposit': 'Deposit',
        'payment': 'Payment',
        'transfer': 'Transfer',
        'bill_payment': 'Bill Payment'
    };
    return types[type] || type;
}

async function loadCardData(target) {
    const element = document.getElementById(target);
    if (!element) return;
    
    element.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`/api/card-data?target=${target}`);
        const data = await response.json();
        
        if (target === 'total-income' || target === 'total-expenses' || target === 'transaction-volume') {
            element.textContent = formatCurrency(data.total || data.volume);
        } 
        else if (target === 'avg-balance') {
            element.textContent = formatCurrency(data.average);
        }
        else if (target === 'total-transactions') {
            element.textContent = data.count;
        }
        else if (target === 'top-sender') {
            element.textContent = data.sender || 'No data';
            if (data.amount) {
                element.nextElementSibling.textContent = `Sent ${formatCurrency(data.amount)}`;
            }
        }
        else if (target === 'top-recipient') {
            element.textContent = data.recipient || 'No data';
            if (data.count) {
                element.nextElementSibling.textContent = `${data.count} transactions`;
            }
        }
        else if (target === 'busiest-hour') {
            element.textContent = data.hour ? `${data.hour}:00` : 'No data';
        }
    } catch (error) {
        element.textContent = 'Error';
        console.error(error);
    }
}

async function loadRecentTransactions() {
    const container = document.getElementById('transactions-list');
    container.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch('/api/recent-transactions');
        const transactions = await response.json();
        
        container.innerHTML = '';
        
        if (transactions.length === 0) {
            container.innerHTML = '<div class="empty-state">No transactions found</div>';
            return;
        }
        
        transactions.forEach(tx => {
            const isIncome = ['receive', 'deposit'].includes(tx.type);
            const txElement = document.createElement('div');
            txElement.className = 'transaction-item';
            
            txElement.innerHTML = `
                <div class="transaction-info">
                    <div class="transaction-icon ${isIncome ? 'income' : 'expense'}">
                        <i class="fas fa-${isIncome ? 'arrow-down' : 'arrow-up'}"></i>
                    </div>
                    <div class="transaction-details">
                        <div class="transaction-title">${formatTransactionType(tx.type)}</div>
                        <div class="transaction-meta">${isIncome ? tx.sender : tx.recipient || 'N/A'}</div>
                    </div>
                </div>
                <div class="transaction-amount ${isIncome ? 'positive' : 'negative'}">
                    ${isIncome ? '+' : '-'}${formatCurrency(tx.amount)}
                </div>
            `;
            
            container.appendChild(txElement);
        });
    } catch (error) {
        container.innerHTML = '<div class="error-state">Failed to load transactions</div>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadRecentTransactions();
    
    document.querySelectorAll('.summary-card, .metric-card').forEach(card => {
        card.style.cursor = 'pointer';
    });
});