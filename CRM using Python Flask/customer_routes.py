from flask import request, jsonify
import pyodbc
from db_config import get_connection_string  

def get_clients_paginated():
    try:
        page = int(request.args.get('page', 1))
        rows_per_page = int(request.args.get('rows', 10))
        offset = (page - 1) * rows_per_page

        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM clients")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT * FROM clients
            ORDER BY id
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """, (offset, rows_per_page))

        # Convert to list of dictionaries
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return jsonify({"total": total, "rows": rows})
    except Exception as e:
        return jsonify({
            "total": 0,
            "rows": [],
            "errorMsg": f"Database error: {str(e)}"
        })
