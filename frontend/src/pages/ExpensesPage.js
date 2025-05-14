import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function ExpensesPage() {
    const { getAccessTokenSilently, isLoading: authLoading, isAuthenticated, user } = useAuth0();

    // --- State for Creating Expense ---
    const [expenseDescription, setExpenseDescription] = useState('');
    const [expenseAmount, setExpenseAmount] = useState('');
    const [expenseCategory, setExpenseCategory] = useState('');
    const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);
    const [isSubmittingExpense, setIsSubmittingExpense] = useState(false);
    const [expenseSubmitError, setExpenseSubmitError] = useState(null);
    const [expenseSubmitSuccess, setExpenseSubmitSuccess] = useState(null);

    // --- State for Fetching Expense by ID ---
    const [expenseIdToFetch, setExpenseIdToFetch] = useState('');
    const [fetchedExpense, setFetchedExpense] = useState(null);
    const [isFetchingExpense, setIsFetchingExpense] = useState(false);
    const [fetchExpenseError, setFetchExpenseError] = useState(null);

    // --- State for Fetching All Expenses ---
    const [allExpenses, setAllExpenses] = useState([]);
    const [isFetchingAllExpenses, setIsFetchingAllExpenses] = useState(false);
    const [fetchAllExpensesError, setFetchAllExpensesError] = useState(null);

    useEffect(() => {
        if (!API_BASE_URL) {
            console.error("REACT_APP_API_BASE_URL is not defined in .env");
            setExpenseSubmitError("API endpoint not configured. Check frontend .env file.");
            setFetchExpenseError("API endpoint not configured. Check frontend .env file.");
        }
    }, []);

    // --- Handler for Creating Expense ---
    const handleExpenseSubmit = async (event) => {
        event.preventDefault();
        if (!isAuthenticated) {
            setExpenseSubmitError("Please log in to submit an expense.");
            return;
        }
        if (!API_BASE_URL) {
            setExpenseSubmitError("API endpoint not configured.");
            return;
        }
        if (!expenseDescription.trim() || !expenseAmount.trim()) {
            setExpenseSubmitError("Description and Amount are required.");
            return;
        }

        setIsSubmittingExpense(true);
        setExpenseSubmitError(null);
        setExpenseSubmitSuccess(null);

        try {
            const token = await getAccessTokenSilently();
            const expenseData = {
                description: expenseDescription,
                amount: expenseAmount,
                category: expenseCategory || null,
                date: expenseDate ? new Date(expenseDate).toISOString() : new Date().toISOString(),
            };

            const response = await axios.post(`${API_BASE_URL}/expenses/create`, expenseData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            setExpenseSubmitSuccess(`Expense "${response.data.description}" added successfully! ID: ${response.data.id}`);
            setExpenseDescription('');
            setExpenseAmount('');
            setExpenseCategory('');
            setExpenseDate(new Date().toISOString().split('T')[0]);
        } catch (error) {
            console.error('Error submitting expense:', error);
            setExpenseSubmitError(
                error.response?.data?.error ||
                error.response?.data?.message ||
                error.message ||
                "Failed to submit expense."
            );
        } finally {
            setIsSubmittingExpense(false);
        }
    };

    // --- Handler for Fetching Expense by ID ---
    const handleFetchExpenseById = async () => {
        if (!isAuthenticated) {
            setFetchExpenseError("Please log in to fetch an expense.");
            return;
        }
        if (!API_BASE_URL) {
            setFetchExpenseError("API endpoint not configured.");
            return;
        }
        if (!expenseIdToFetch || isNaN(parseInt(expenseIdToFetch, 10))) {
            setFetchExpenseError("Please enter a valid numeric Expense ID.");
            setFetchedExpense(null);
            return;
        }

        setIsFetchingExpense(true);
        setFetchExpenseError(null);
        setFetchedExpense(null);

        try {
            const token = await getAccessTokenSilently();
            const response = await axios.get(
                `${API_BASE_URL}/expenses/get_by_id/${expenseIdToFetch}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            setFetchedExpense(response.data);
        } catch (error) {
            console.error('Error fetching expense by ID:', error);
            setFetchExpenseError(
                error.response?.data?.error ||
                error.response?.data?.message ||
                error.message ||
                "Failed to fetch expense."
            );
        } finally {
            setIsFetchingExpense(false);
        }
    };

    // --- Handler for Fetching All Expenses ---
    const handleFetchAllExpenses = async () => {
        if (!isAuthenticated) {
            setFetchAllExpensesError("Please log in to fetch expenses.");
            return;
        }
        if (!API_BASE_URL) {
            setFetchAllExpensesError("API endpoint not configured.");
            return;
        }

        setIsFetchingAllExpenses(true);
        setFetchAllExpensesError(null);
        setAllExpenses([]);

        try {
            const token = await getAccessTokenSilently();
            const response = await axios.get(`${API_BASE_URL}/expenses/get_all`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setAllExpenses(response.data || []);
        } catch (error) {
            console.error('Error fetching all expenses:', error);
            setFetchAllExpensesError(
                error.response?.data?.error ||
                error.response?.data?.message ||
                error.message ||
                "Failed to fetch expenses."
            );
        } finally {
            setIsFetchingAllExpenses(false);
        }
    };

    if (authLoading) {
        return <div className="page-loading">Loading authentication...</div>;
    }

    if (!isAuthenticated) {
        return <div className="page-container">Please log in to manage expenses.</div>;
    }

    return (
        <div className="page-container expense-page" style={{ padding: '20px' }}>
            <h2>Manage Expenses</h2>
            <p>Welcome, {user?.name || user?.nickname || user?.email}!</p>

            {/* --- Section for Adding New Expense --- */}
            <div className="expense-form-section" style={{ marginTop: '30px', border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
                <h3>Add New Expense</h3>
                <form onSubmit={handleExpenseSubmit}>
                    <div>
                        <label htmlFor="expenseDate">Date:</label>
                        <input
                            type="date"
                            id="expenseDate"
                            value={expenseDate}
                            onChange={(e) => setExpenseDate(e.target.value)}
                            required
                            style={{ display: 'block', marginBottom: '10px', width: '300px', padding: '8px' }}
                        />
                    </div>
                    <div>
                        <label htmlFor="expenseDescription">Description:</label>
                        <input
                            type="text"
                            id="expenseDescription"
                            value={expenseDescription}
                            onChange={(e) => setExpenseDescription(e.target.value)}
                            placeholder="e.g., Coffee with client"
                            required
                            maxLength="200"
                            style={{ display: 'block', marginBottom: '10px', width: '300px', padding: '8px' }}
                        />
                    </div>
                    <div>
                        <label htmlFor="expenseAmount">Amount:</label>
                        <input
                            type="number"
                            id="expenseAmount"
                            value={expenseAmount}
                            onChange={(e) => setExpenseAmount(e.target.value)}
                            placeholder="e.g., 4.50"
                            required
                            step="0.01"
                            min="0.01"
                            style={{ display: 'block', marginBottom: '10px', width: '300px', padding: '8px' }}
                        />
                    </div>
                    <div>
                        <label htmlFor="expenseCategory">Category (Optional):</label>
                        <input
                            type="text"
                            id="expenseCategory"
                            value={expenseCategory}
                            onChange={(e) => setExpenseCategory(e.target.value)}
                            placeholder="e.g., Meals, Travel"
                            maxLength="50"
                            style={{ display: 'block', marginBottom: '10px', width: '300px', padding: '8px' }}
                        />
                    </div>
                    <button type="submit" disabled={isSubmittingExpense || authLoading} style={{ padding: '10px 15px' }}>
                        {isSubmittingExpense ? 'Adding Expense...' : 'Add Expense'}
                    </button>
                </form>
                {expenseSubmitSuccess && <p style={{ color: 'green', marginTop: '10px' }}>{expenseSubmitSuccess}</p>}
                {expenseSubmitError && <p style={{ color: 'red', marginTop: '10px' }}>Error: {expenseSubmitError}</p>}
            </div>

            {/* --- Section for Fetching Expense by ID --- */}
            <div className="fetch-expense-section" style={{ marginTop: '30px', border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
                <h3>Get Expense by ID</h3>
                <div>
                    <input
                        type="number"
                        value={expenseIdToFetch}
                        onChange={(e) => setExpenseIdToFetch(e.target.value)}
                        placeholder="Enter Expense ID"
                        style={{ marginRight: '10px', padding: '8px' }}
                    />
                    <button onClick={handleFetchExpenseById} disabled={isFetchingExpense || authLoading} style={{ padding: '10px 15px' }}>
                        {isFetchingExpense ? 'Fetching...' : 'Fetch Expense'}
                    </button>
                </div>

                {fetchExpenseError && (
                    <p style={{ color: 'red', marginTop: '10px' }}>Error: {fetchExpenseError}</p>
                )}

                {fetchedExpense && (
                    <div style={{ marginTop: '15px', border: '1px solid #eee', padding: '10px', backgroundColor: '#f9f9f9' }}>
                        <h4>Fetched Expense Details:</h4>
                        <pre>{JSON.stringify(fetchedExpense, null, 2)}</pre>
                    </div>
                )}
            </div>

            {/* --- Section for Fetching All Expenses --- */}
            <div className="fetch-all-expenses-section" style={{ marginTop: '30px', border: '1px solid #ddd', padding: '20px', borderRadius: '8px' }}>
                <h3>All Expenses</h3>
                <button onClick={handleFetchAllExpenses} disabled={isFetchingAllExpenses || authLoading} style={{ padding: '10px 15px' }}>
                    {isFetchingAllExpenses ? 'Loading...' : 'Fetch All Expenses'}
                </button>

                {fetchAllExpensesError && (
                    <p style={{ color: 'red', marginTop: '10px' }}>Error: {fetchAllExpensesError}</p>
                )}

                {allExpenses.length > 0 && (
                    <div style={{ marginTop: '15px', border: '1px solid #eee', padding: '10px', backgroundColor: '#f0f8ff' }}>
                        <h4>All Expenses:</h4>
                        <pre>{JSON.stringify(allExpenses, null, 2)}</pre>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ExpensesPage;
