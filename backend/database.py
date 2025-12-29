import sqlite3

DB_PATH = "jobs.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            url TEXT NOT NULL,
            platform TEXT NOT NULL,
            location TEXT,
            experience TEXT,
            education TEXT,
            salary TEXT,
            deadline TEXT,
            job_type TEXT,
            intern_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 데이터베이스 초기화 완료")


def save_job(job_data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs 
            (job_id, title, company, url, platform, location, experience, education, salary, deadline, job_type, intern_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('job_id'),
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('url'),
            job_data.get('platform'),
            job_data.get('location'),
            job_data.get('experience'),
            job_data.get('education'),
            job_data.get('salary'),
            job_data.get('deadline'),
            job_data.get('job_type', 'IT'),
            job_data.get('intern_type', '인턴')
        ))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 저장 오류: {e}")
        return False
    finally:
        conn.close()


def get_all_jobs(platform=None, intern_type=None, limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if platform and platform != "전체":
        query += " AND platform = ?"
        params.append(platform)

    if intern_type and intern_type != "전체":
        query += " AND intern_type = ?"
        params.append(intern_type)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs


def get_job_count_by_platform():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT platform, COUNT(*) as count 
        FROM jobs 
        GROUP BY platform
    ''')
    result = {row['platform']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return result


def get_job_count_by_intern_type():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT intern_type, COUNT(*) as count 
        FROM jobs 
        GROUP BY intern_type
    ''')
    result = {row['intern_type']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return result
