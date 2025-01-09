// Chart instances store
let charts = {
    salesTrend: null,
    categoryPerformance: null,
    productPerformance: null
};

// Constants
const CHART_COLORS = {
    primary: '#720455',
    secondary: '#3C0753',
    accent: '#4361ee',
    error: '#ef4444',
    background: 'rgba(255, 255, 255, 0.1)',
    chartColors: [
        '#4361ee',
        '#ef4444',
        '#3b82f6',
        '#10b981',
        '#f59e0b',
        '#8b5cf6'
    ]
};

const CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: { color: '#fff' }
        }
    },
    scales: {
        y: {
            grid: { color: CHART_COLORS.background },
            ticks: { color: '#fff' }
        },
        x: {
            grid: { color: CHART_COLORS.background },
            ticks: { color: '#fff' }
        }
    }
};

// Utility Functions
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

function calculateGrowthRate(current, previous) {
    if (!previous) return 0;
    return ((current - previous) / previous) * 100;
}

// Data Processing Functions
function parseCSV(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1)
        .filter(line => line.trim())
        .map(line => {
            const values = line.split(',');
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index]?.trim() || '';
            });
            return row;
        });
}

function validateData(data) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        throw new Error('Invalid data format: Data must be a non-empty array');
    }

    const requiredColumns = ['Amount', 'Profit', 'Quantity', 'PaymentMode', 'Category', 'SubCategory', 'Month'];
    const headers = Object.keys(data[0] || {});
    const missingColumns = requiredColumns.filter(col => !headers.includes(col));

    if (missingColumns.length > 0) {
        throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
    }

    const invalidRows = data.filter(row => {
        return isNaN(parseFloat(row.Amount)) || 
               isNaN(parseFloat(row.Profit)) || 
               isNaN(parseFloat(row.Quantity));
    });

    if (invalidRows.length > 0) {
        throw new Error('Invalid data: Amount, Profit, and Quantity must be numbers');
    }
}

// Analytics Functions
function calculateKPIs(data) {
    const totalOrders = data.length;
    const totalAmount = data.reduce((sum, row) => sum + parseFloat(row.Amount), 0);
    const totalProfit = data.reduce((sum, row) => sum + parseFloat(row.Profit), 0);
    const totalQuantity = data.reduce((sum, row) => sum + parseFloat(row.Quantity), 0);

    return {
        conversionRate: (totalOrders / (totalOrders * 1.5)) * 100,
        avgOrderValue: totalAmount / totalOrders,
        profitMargin: (totalProfit / totalAmount) * 100,
        avgQuantityPerOrder: totalQuantity / totalOrders
    };
}

function createSalesTrendChart(data) {
    if (charts.salesTrend) {
        charts.salesTrend.destroy();
    }

    const monthlyData = data.reduce((acc, row) => {
        const month = row.Month;
        if (!acc[month]) {
            acc[month] = {
                sales: 0,
                profit: 0
            };
        }
        acc[month].sales += parseFloat(row.Amount);
        acc[month].profit += parseFloat(row.Profit);
        return acc;
    }, {});

    const months = Object.keys(monthlyData);
    const sales = months.map(month => monthlyData[month].sales);
    const profits = months.map(month => monthlyData[month].profit);

    // Calculate trend line
    const salesPoints = sales.map((y, i) => [i, y]);
    const salesTrend = regression.linear(salesPoints);
    const salesTrendLine = months.map((_, i) => salesTrend.predict(i)[1]);

    const ctx = document.getElementById('salesTrendChart').getContext('2d');
    charts.salesTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Sales',
                data: sales,
                borderColor: CHART_COLORS.accent,
                tension: 0.4,
                fill: false
            }, {
                label: 'Profit',
                data: profits,
                borderColor: CHART_COLORS.chartColors[1],
                tension: 0.4,
                fill: false
            }, {
                label: 'Sales Trend',
                data: salesTrendLine,
                borderColor: CHART_COLORS.chartColors[2],
                borderDash: [5, 5],
                tension: 0,
                fill: false
            }]
        },
        options: {
            ...CHART_OPTIONS,
            plugins: {
                ...CHART_OPTIONS.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${context.raw.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

function createCategoryPerformanceChart(data) {
    if (charts.categoryPerformance) {
        charts.categoryPerformance.destroy();
    }

    const categoryData = data.reduce((acc, row) => {
        if (!acc[row.Category]) {
            acc[row.Category] = { sales: 0, profit: 0, quantity: 0 };
        }
        acc[row.Category].sales += parseFloat(row.Amount);
        acc[row.Category].profit += parseFloat(row.Profit);
        acc[row.Category].quantity += parseFloat(row.Quantity);
        return acc;
    }, {});

    const categories = Object.keys(categoryData);
    const profitMargins = categories.map(cat => 
        (categoryData[cat].profit / categoryData[cat].sales) * 100
    );
    const sales = categories.map(cat => categoryData[cat].sales);
    const quantities = categories.map(cat => categoryData[cat].quantity);

    const ctx = document.getElementById('categoryPerformanceChart').getContext('2d');
    charts.categoryPerformance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Sales',
                data: sales,
                backgroundColor: CHART_COLORS.accent,
                yAxisID: 'y'
            }, {
                label: 'Profit Margin %',
                data: profitMargins,
                type: 'line',
                borderColor: CHART_COLORS.error,
                backgroundColor: 'transparent',
                yAxisID: 'y1'
            }, {
                label: 'Quantity',
                data: quantities,
                backgroundColor: CHART_COLORS.chartColors[2],
                yAxisID: 'y2'
            }]
        },
        options: {
            ...CHART_OPTIONS,
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Sales (₹)',
                        color: '#fff'
                    },
                    grid: { color: CHART_COLORS.background },
                    ticks: { color: '#fff' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Profit Margin (%)',
                        color: '#fff'
                    },
                    grid: { display: false },
                    ticks: { color: '#fff' }
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Quantity',
                        color: '#fff'
                    },
                    grid: { display: false },
                    ticks: { color: '#fff' }
                }
            }
        }
    });
}

function createProductPerformanceMatrix(data) {
    if (charts.productPerformance) {
        charts.productPerformance.destroy();
    }

    const productData = data.reduce((acc, row) => {
        if (!acc[row.SubCategory]) {
            acc[row.SubCategory] = {
                quantity: 0,
                profit: 0,
                revenue: 0
            };
        }
        acc[row.SubCategory].quantity += parseFloat(row.Quantity);
        acc[row.SubCategory].profit += parseFloat(row.Profit);
        acc[row.SubCategory].revenue += parseFloat(row.Amount);
        return acc;
    }, {});

    const products = Object.keys(productData);
    const datasets = products.map(product => ({
        x: productData[product].quantity,
        y: productData[product].profit,
        r: Math.sqrt(productData[product].revenue) / 20,
        label: product
    }));

    const ctx = document.getElementById('productPerformanceChart').getContext('2d');
    charts.productPerformance = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Products',
                data: datasets,
                backgroundColor: datasets.map((_, i) => 
                    CHART_COLORS.chartColors[i % CHART_COLORS.chartColors.length]
                )
            }]
        },
        options: {
            ...CHART_OPTIONS,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Profit (₹)',
                        color: '#fff'
                    },
                    grid: { color: CHART_COLORS.background },
                    ticks: { color: '#fff' }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Quantity Sold',
                        color: '#fff'
                    },
                    grid: { color: CHART_COLORS.background },
                    ticks: { color: '#fff' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const data = context.raw;
                            return [
                                `Product: ${data.label}`,
                                `Quantity: ${data.x}`,
                                `Profit: ₹${data.y.toFixed(2)}`,
                                `Revenue: ₹${(data.r * 20) ** 2}`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function createPaymentAnalysis(data) {
    const paymentData = data.reduce((acc, row) => {
        if (!acc[row.PaymentMode]) {
            acc[row.PaymentMode] = {
                amount: 0,
                count: 0,
                profit: 0
            };
        }
        acc[row.PaymentMode].amount += parseFloat(row.Amount);
        acc[row.PaymentMode].count += 1;
        acc[row.PaymentMode].profit += parseFloat(row.Profit);
        return acc;
    }, {});

    const tableBody = document.getElementById('paymentAnalysisTable').querySelector('tbody');
    tableBody.innerHTML = '';

    Object.entries(paymentData)
        .sort((a, b) => b[1].amount - a[1].amount)
        .forEach(([mode, data]) => {
            const row = tableBody.insertRow();
            row.insertCell(0).textContent = mode;
            row.insertCell(1).textContent = formatCurrency(data.amount);
            row.insertCell(2).textContent = data.count;
            row.insertCell(3).textContent = formatCurrency(data.profit);
            
            const avgTransaction = data.amount / data.count;
            const trendCell = row.insertCell(4);
            const trendIndicator = document.createElement('span');
            trendIndicator.className = `trend-indicator ${avgTransaction > 3000 ? 'trend-up' : 'trend-down'}`;
            trendIndicator.textContent = avgTransaction > 3000 ? '↑' : '↓';
            trendCell.appendChild(trendIndicator);
        });
}

function generateInsights(data) {
    const insights = [];

    // Category Performance
    const categoryPerformance = data.reduce((acc, row) => {
        if (!acc[row.Category]) {
            acc[row.Category] = { sales: 0, profit: 0 };
        }
        acc[row.Category].sales += parseFloat(row.Amount);
        acc[row.Category].profit += parseFloat(row.Profit);
        return acc;
    }, {});

    const bestCategory = Object.entries(categoryPerformance)
        .sort((a, b) => b[1].profit - a[1].profit)[0];

    insights.push({
        title: 'Top Performing Category',
        description: `${bestCategory[0]} is the best performing category with ${formatCurrency(bestCategory[1].profit)} in profits.`
    });

    // Payment Analysis
    const paymentModes = data.reduce((acc, row) => {
        acc[row.PaymentMode] = (acc[row.PaymentMode] || 0) + parseFloat(row.Amount);
        return acc;
    }, {});

    const preferredPayment = Object.entries(paymentModes)
        .sort((a, b) => b[1] - a[1])[0];

    insights.push({
        title: 'Preferred Payment Method',
        description: `${preferredPayment[0]} is the most used payment method with ${formatCurrency(preferredPayment[1])} in transactions.`
    });

    // Monthly Trend
    const monthlyTrend = data.reduce((acc, row) => {
        acc[row.Month] = (acc[row.Month] || 0) + parseFloat(row.Amount);
        return acc;
    }, {});

    const months = Object.keys(monthlyTrend);
    const lastMonth = months[months.length - 1];
    const previousMonth = months[months.length - 2];
    
    if (lastMonth && previousMonth) {
        const growth = calculateGrowthRate(monthlyTrend[lastMonth], monthlyTrend[previousMonth]);
        insights.push({
            title: 'Monthly Growth',
            description: `Sales ${growth > 0 ? 'increased' : 'decreased'} by ${Math.abs(growth).toFixed(1)}% from ${previousMonth} to ${lastMonth}.`
        });
    }

    return insights;
}

// Export functions
window.Analytics = {
    parseCSV,
    validateData,
    calculateKPIs,
    createSalesTrendChart,
    createCategoryPerformanceChart,
    createPaymentAnalysis,
    createProductPerformanceMatrix,
    generateInsights,
    formatCurrency,
    charts
};
