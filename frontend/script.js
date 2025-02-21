// Sample data for charts
const expensesData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [{
        label: "Monthly Expenses",
        data: [900, 800, 450, 300, 150, 0],
        backgroundColor: "#007bff",
    }],
};

const distributionData = {
    labels: ["Send Money", "Airtime", "Bank", "Bills", "Merchant"], // Updated categories
    datasets: [{
        label: "Expense Distribution",
        data: [300, 200, 150, 100, 50], // Sample data for each category
        backgroundColor: ["#007bff", "#28a745", "#ffc107", "#dc3545", "#6f42c1"], // Different colors for each category
    }],
};

// Render Bar Chart (Monthly Expenses)
const expensesChart = new Chart(document.getElementById("expensesChart"), {
    type: "bar",
    data: expensesData,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
            },
        },
    },
});

// Render Pie Chart (Expense Distribution)
const distributionChart = new Chart(document.getElementById("distributionChart"), {
    type: "pie", // Changed to pie chart
    data: distributionData,
    options: {
        responsive: true,
    },
<<<<<<< HEAD
});
=======
});
>>>>>>> 37616bef472042491c83770a5c7054eaccee9efd
