import React, { useState, useEffect } from 'react';
import { customerService } from '../services/api';
import CustomerForm from './CustomerForm';
import './CustomerDashboard.css';

function CustomerDashboard() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCustomers, setTotalCustomers] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [currentCustomer, setCurrentCustomer] = useState(null);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await customerService.getCustomers(page, rowsPerPage);
      
      if (response.success) {
        setCustomers(response.customers);
        setTotalCustomers(response.total);
      } else {
        setError(response.message || 'Failed to fetch customers');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, rowsPerPage]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(1);
  };

  const openAddModal = () => {
    setCurrentCustomer(null);
    setShowModal(true);
  };

  const openEditModal = (customer) => {
    setCurrentCustomer(customer);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  const handleSave = async (customerData) => {
    try {
      if (currentCustomer) {
        // Update existing customer
        await customerService.updateCustomer(currentCustomer.id, customerData);
      } else {
        // Create new customer
        await customerService.createCustomer(customerData);
      }
      
      closeModal();
      fetchCustomers();
    } catch (err) {
      console.error('Error saving customer:', err);
      alert(`Failed to save customer: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await customerService.deleteCustomer(id);
        fetchCustomers();
      } catch (err) {
        console.error('Error deleting customer:', err);
        alert(`Failed to delete customer: ${err.message}`);
      }
    }
  };

  const totalPages = Math.ceil(totalCustomers / rowsPerPage);

  return (
    <div className="customer-dashboard">
      <div className="dashboard-header">
        <h1>Customer Management</h1>
        <button className="add-button" onClick={openAddModal}>
          Add New Customer
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <>
          <div className="customer-table-container">
            <table className="customer-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Mobile</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="no-data">No customers found</td>
                  </tr>
                ) : (
                  customers.map((customer) => (
                    <tr key={customer.id}>
                      <td>{customer.id}</td>
                      <td>{customer.name}</td>
                      <td>{customer.email}</td>
                      <td>{customer.mobile}</td>
                      <td>{customer.company}</td>
                      <td>
                        <span className={`status-badge ${customer.status?.toLowerCase()}`}>
                          {customer.status || 'N/A'}
                        </span>
                      </td>
                      <td className="actions">
                        <button 
                          className="edit-button" 
                          onClick={() => openEditModal(customer)}
                        >
                          Edit
                        </button>
                        <button 
                          className="delete-button"
                          onClick={() => handleDelete(customer.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <div className="pagination">
            <div className="rows-per-page">
              <label>
                Rows per page:
                <select 
                  value={rowsPerPage} 
                  onChange={handleRowsPerPageChange}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                </select>
              </label>
            </div>
            
            <div className="page-navigation">
              <button 
                disabled={page === 1} 
                onClick={() => handlePageChange(page - 1)}
              >
                Previous
              </button>
              
              <span className="page-info">
                Page {page} of {totalPages || 1}
              </span>
              
              <button 
                disabled={page >= totalPages} 
                onClick={() => handlePageChange(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>{currentCustomer ? 'Edit Customer' : 'Add New Customer'}</h2>
              <button className="close-button" onClick={closeModal}>×</button>
            </div>
            <CustomerForm 
              customer={currentCustomer} 
              onSave={handleSave} 
              onCancel={closeModal} 
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomerDashboard;