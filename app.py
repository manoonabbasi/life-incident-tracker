import os
import time
from datetime import datetime
from flask import send_from_directory
from flask import Flask, request, render_template, redirect, flash, url_for, render_template_string
from werkzeug.utils import secure_filename
import sqlite3
from pysqlcipher3 import dbapi2 as sqlite

from config import DB_PASSWORD, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, CATEGORIES

# Initialize app
app = Flask(__name__)
app.secret_key = DB_PASSWORD
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Custom template filter
@app.template_filter('month_name')
def month_name_filter(month_num):
    import calendar
    try:
        return calendar.month_name[int(month_num)]
    except:
        return str(month_num)

@app.context_processor
def inject_utilities():
    return {'datetime': datetime, 'now': datetime.now, 'strftime': datetime.strftime}

# Database functions
def get_db():
    try:
        conn = sqlite.connect('life_incidents.db')
        conn.execute(f"PRAGMA key='{DB_PASSWORD}'")
        conn.execute("PRAGMA cipher_compatibility=4")
        conn.set_trace_callback(print)
        return conn
    except Exception as e:
        app.logger.error(f"DB Connection failed: {str(e)}")
        raise

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            attachment TEXT
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON incidents(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON incidents(category)")
        conn.commit()

# Helper to check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def home():
    try:
        query = """
        SELECT id, strftime('%Y-%m-%d %H:%M', date) as formatted_date, title, description, category, attachment
        FROM incidents
        """
        conditions = []
        params = []

        if request.args.get('year'):
            conditions.append("strftime('%Y', date) = ?")
            params.append(request.args['year'])
        if request.args.get('month'):
            month = request.args['month'].zfill(2)
            conditions.append("strftime('%m', date) = ?")
            params.append(month)
        if request.args.get('category'):
            conditions.append("category = ?")
            params.append(request.args['category'])
        if request.args.get('search'):
            search = f"%{request.args['search']}%"
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([search, search])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY date DESC"

        with get_db() as conn:
            incidents = conn.execute(query, params).fetchall()
            years = [row[0] for row in conn.execute("SELECT DISTINCT strftime('%Y', date) FROM incidents ORDER BY date DESC")]

        return render_template('dashboard.html',
                               incidents=incidents,
                               years=years,
                               categories=CATEGORIES,
                               current_filters=request.args,
                               datetime=datetime,
                               months=range(1, 13))

    except Exception as e:
        app.logger.error(f"Home route error: {str(e)}")
        return render_template('dashboard.html',
                               incidents=[],
                               years=[],
                               categories=CATEGORIES,
                               current_filters={},
                               datetime=datetime,
                               months=range(1, 13))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/add', methods=['POST'])
def add_incident():
    try:
        if not request.form.get('title'):
            flash("Title is required", "error")
            return redirect(url_for('home'))

        date = request.form.get('date') or datetime.now().strftime("%Y-%m-%d")
        time_str = request.form.get('time') or datetime.now().strftime("%H:%M")
        datetime_str = f"{date} {time_str}"

        attachment_filename = None
        file = request.files.get('attachment')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            attachment_filename = filename

        with get_db() as conn:
            conn.execute(
                "INSERT INTO incidents (date, title, description, category, attachment) VALUES (?, ?, ?, ?, ?)",
                (datetime_str,
                 request.form['title'],
                 request.form.get('description', ''),
                 request.form.get('category', CATEGORIES[0]),
                 attachment_filename)
            )
            conn.commit()

        flash("Incident added successfully!", "success")

    except Exception as e:
        flash(f"Failed to save: {str(e)}", "error")
        app.logger.error(f"Add incident error: {str(e)}")

    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_incident(id):
    with get_db() as conn:
        if request.method == 'POST':
            # Process form data
            title = request.form['title']
            description = request.form.get('description', '')
            category = request.form.get('category', '')
            attachment = None

            # Handle attachment upload if provided
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file and file.filename != '':
                    filename = file.filename
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(save_path)
                    attachment = filename

            # Build update query
            if attachment:
                conn.execute("""
                    UPDATE incidents
                    SET title = ?, description = ?, category = ?, attachment = ?
                    WHERE id = ?
                """, (title, description, category, attachment, id))
            else:
                conn.execute("""
                    UPDATE incidents
                    SET title = ?, description = ?, category = ?
                    WHERE id = ?
                """, (title, description, category, id))
            conn.commit()

            flash("Incident updated successfully!", "success")
            return redirect(url_for('home'))

        else:
            # Show edit form
            incident = conn.execute("""
                SELECT id, date, title, description, category, attachment
                FROM incidents
                WHERE id = ?
            """, (id,)).fetchone()
            if not incident:
                flash("Incident not found", "error")
                return redirect(url_for('home'))

            return render_template('edit_incident.html',
                                   incident=incident,
                                   categories=CATEGORIES)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_incident(id):
    with get_db() as conn:
        conn.execute("DELETE FROM incidents WHERE id = ?", (id,))
        conn.commit()
    flash("Incident deleted successfully!", "success")
    return redirect(url_for('home'))


@app.route('/debug-db')
def debug_db():
    try:
        with get_db() as conn:
            incidents = conn.execute("""
                SELECT id, date, title, category, attachment 
                FROM incidents 
                ORDER BY date DESC
            """).fetchall()
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]

        return render_template_string('''
            <h1>Database Debug</h1>
            <h3>Tables ({{ tables|length }})</h3>
            <ul>{% for table in tables %}<li>{{ table[0] }}</li>{% endfor %}</ul>
            <h3>Incidents ({{ count }})</h3>
            <table border=1>
                <tr><th>ID</th><th>Date</th><th>Title</th><th>Category</th><th>Attachment</th></tr>
                {% for i in incidents %}
                <tr>
                    <td>{{ i[0] }}</td><td>{{ i[1] }}</td><td>{{ i[2] }}</td><td>{{ i[3] }}</td><td>{{ i[4] }}</td>
                </tr>
                {% else %}<tr><td colspan=5>No incidents</td></tr>{% endfor %}
            </table>
        ''', incidents=incidents, tables=tables, count=count)

    except Exception as e:
        return f"<h1>DB Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5032, debug=True)

