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

function setupSearch() {
    const searchButton = document.getElementById('searchButton');
    const resetButton = document.getElementById('resetButton');
    
    searchButton.addEventListener('click', executeSearch);
    resetButton.addEventListener('click', resetSearch);
    
    document.querySelectorAll('.search-filters input').forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') executeSearch();
        });
    });
}

function renderTransactions(transactions) {
    const container = document.getElementById('transactions-list');
    container.innerHTML = '';

    if (!transactions || transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No transactions found</p>
            </div>
        `;
        return;
    }

    transactions.forEach(transaction => {
        const isIncome = ['receive', 'deposit'].includes(transaction.type);
        const transactionElement = document.createElement('div');
        transactionElement.className = 'transaction-item';
        
        transactionElement.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-icon ${isIncome ? 'income' : 'expense'}">
                    <i class="fas fa-${isIncome ? 'arrow-down' : 'arrow-up'}"></i>
                </div>
                <div class="transaction-details">
                    <div class="transaction-title">${formatTransactionType(transaction.type)}</div>
                    <div class="transaction-meta">
                        ${transaction.sender || transaction.recipient || 'N/A'}
                    </div>
                </div>
            </div>
            <div class="transaction-amount ${isIncome ? 'positive' : 'negative'}">
                ${isIncome ? '+' : '-'}${formatCurrency(transaction.amount)}
            </div>
            <div class="transaction-date">
                ${new Date(transaction.timestamp).toLocaleDateString()}
            </div>
        `;
        
        container.appendChild(transactionElement);
    });
}

function formatTransactionType(type) {
    const typeMap = {
        'payment': 'Payment',
        'deposit': 'Deposit',
        'transfer': 'Transfer',
        'receive': 'Received',
        'bill_payment': 'Bill Payment'
    };
    return typeMap[type] || type;
}

function formatCurrency(amount) {
    return 'RWF ' + (amount || 0).toLocaleString('en-RW');
}

async function executeSearch() {
    try {
        const transactionsList = document.getElementById('transactions-list');
        transactionsList.innerHTML = '<div class="loading-spinner large"></div>';
        
        const params = new URLSearchParams();
        
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;
        const minAmount = document.getElementById('minAmount').value;
        const maxAmount = document.getElementById('maxAmount').value;
        const transactionType = document.getElementById('transactionType').value;
        
        if (dateFrom) params.append('dateFrom', dateFrom);
        if (dateTo) params.append('dateTo', dateTo);
        
        if (minAmount) {
            if (isNaN(minAmount)) throw new Error("Minimum amount must be a number");
            params.append('minAmount', minAmount);
        }
        if (maxAmount) {
            if (isNaN(maxAmount)) throw new Error("Maximum amount must be a number");
            params.append('maxAmount', maxAmount);
        }
        
        if (transactionType) params.append('type', transactionType);
        
        const response = await fetch(`/api/transactions/search?${params.toString()}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Search failed");
        }
        
        const transactions = await response.json();
        renderTransactions(transactions);
        
    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('transactions-list').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${error.message || 'Failed to load search results'}</p>
            </div>
        `;
    }
}

function resetSearch() {
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    document.getElementById('minAmount').value = '';
    document.getElementById('maxAmount').value = '';
    document.getElementById('transactionType').value = '';
    
    loadRecentTransactions();
}

document.addEventListener('DOMContentLoaded', function() {
    loadRecentTransactions();
    
    document.querySelectorAll('.summary-card, .metric-card').forEach(card => {
        card.style.cursor = 'pointer';
    });
    setupSearch();
});