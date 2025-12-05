import sqlite3
import os

def check_materials_sqlite():
    db_path = 'backend/uma_audit.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        # Try root
        db_path = 'uma_audit.db'
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return

    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table structure first to ensure columns exist
    cursor.execute("PRAGMA table_info(base_materials)")
    columns = [info[1] for info in cursor.fetchall()]
    print("Columns in base_materials:", columns)
    
    required_cols = ['price_date', 'price_type', 'region', 'province', 'city']
    available_cols = [c for c in required_cols if c in columns]
    
    print(f"Grouping by: {available_cols}")
    
    group_by_clause = ", ".join(available_cols)
    select_clause = ", ".join(available_cols)
    
    query = f"""
    SELECT {select_clause}, count(*) as count
    FROM base_materials
    WHERE price_date IS NOT NULL
    GROUP BY {group_by_clause}
    ORDER BY price_date DESC
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print("\nResults:")
        print(f"{' | '.join(available_cols)} | Count")
        print("-" * 80)
        for row in rows:
            print(f"{' | '.join(str(x) for x in row)}")
            
        # Get total count
        cursor.execute("SELECT count(*) FROM base_materials")
        total = cursor.fetchone()[0]
        print("-" * 80)
        print(f"Total materials: {total}")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_materials_sqlite()

