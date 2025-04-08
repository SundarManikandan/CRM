let editingIndex = undefined;

function endEditing() {
    if (editingIndex === undefined) return true;
    if ($('#dg').datagrid('validateRow', editingIndex)) {
        $('#dg').datagrid('endEdit', editingIndex);
        editingIndex = undefined;
        return true;
    }
    return false;
}

function addRow() {
    if (endEditing()) {
        $('#dg').datagrid('appendRow', {
            name: '', mobile: '', email: '', gstin: '', address: '',
            pincode: '', contact_person: '', company: '', state: '',
            country: '', status: ''
        });
        editingIndex = $('#dg').datagrid('getRows').length - 1;
        $('#dg').datagrid('selectRow', editingIndex).datagrid('beginEdit', editingIndex);
    }
}

function editRow() {
    const row = $('#dg').datagrid('getSelected');
    if (row) {
        editingIndex = $('#dg').datagrid('getRowIndex', row);
        $('#dg').datagrid('beginEdit', editingIndex);
    } else {
        alert("Please select a row to edit.");
    }
}

function saveRow() {
    if (!endEditing()) return;

    const row = $('#dg').datagrid('getSelected');
    if (!row) {
        alert("Please select a row to save.");
        return;
    }

    const url = row.id ? '/update_user' : '/save_user';

    $.post(url, row, function (res) {
        try {
            const data = typeof res === 'string' ? JSON.parse(res) : res;
            if (data.success) {
                $('#dg').datagrid('reload');
                alert("Saved successfully");
            } else {
                alert(data.errorMsg || "Save failed");
            }
        } catch (err) {
            alert("Invalid response from server.");
            console.error(res);
        }
    });
}

function deleteRow() {
    const row = $('#dg').datagrid('getSelected');
    if (row && row.id) {
        if (confirm("Are you sure to delete this customer?")) {
            $.post('/delete_user', { id: row.id }, function (res) {
                const data = typeof res === 'string' ? JSON.parse(res) : res;
                if (data.success) {
                    $('#dg').datagrid('reload');
                    alert("Deleted successfully");
                } else {
                    alert(data.errorMsg || "Delete failed");
                }
            });
        }
    } else {
        alert("Please select a row to delete.");
    }
}

async function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape' });

    const data = $('#dg').datagrid('getRows').filter(row => row && row.name);
    if (!data.length) {
        alert("No data available to export.");
        return;
    }

    const columns = $('#dg').datagrid('getColumnFields')
        .filter(field => field !== 'id')
        .map(field => {
            const col = $('#dg').datagrid('getColumnOption', field);
            return { header: col.title, dataKey: field };
        });

    const rows = data.map(row => {
        const newRow = {};
        columns.forEach(col => {
            newRow[col.dataKey] = row[col.dataKey] ?? '';
        });
        return newRow;
    });

    doc.setFontSize(14);
    doc.text("Customer List", 14, 15);
    const dateStr = new Date().toLocaleString();
    doc.setFontSize(10);
    doc.text(`Generated on: ${dateStr}`, 230, 15);

    doc.autoTable({
        startY: 20,
        headStyles: { fillColor: [22, 160, 133], halign: 'center' },
        styles: { fontSize: 8, cellPadding: 2, overflow: 'linebreak' },
        columnStyles: { email: { cellWidth: 40 }, address: { cellWidth: 50 } },
        columns: columns,
        body: rows
    });

    doc.save("customer_list.pdf");
}

function submitLogin() {
    const username = $('#username').textbox('getValue');
    const password = $('#password').passwordbox('getValue');

    $.post('/login', { username, password }, function (res) {
        if (res.success) {
            window.location.href = '/';
        } else {
            $('#error-msg').text(res.errorMsg || 'Login failed').fadeIn();
        }
    }).fail(() => {
        $('#error-msg').text('Server error. Please try again.').fadeIn();
    });
}
