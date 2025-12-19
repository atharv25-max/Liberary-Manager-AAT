import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. CONFIGURATION (Must be the first command) ---
st.set_page_config(
    page_title="Smart Library System",
    page_icon="📚",
    layout="wide"
)

# --- CUSTOM CSS FOR DARK MODE & STYLING ---
st.markdown("""
    <style>
        /* Main Background */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }
        
        /* Headings */
        h1, h2, h3 {
            color: #FF4B4B !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
        }
        
        /* Metrics Cards */
        div[data-testid="stMetric"] {
            background-color: #1F2937;
            border: 1px solid #374151;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
            transition: transform 0.2s;
        }
        div[data-testid="stMetric"]:hover {
            transform: scale(1.02);
            border-color: #FF4B4B;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #FF4B4B 0%, #FF914D 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px 0 rgba(255, 75, 75, 0.39);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 75, 75, 0.23);
        }
        
        /* Input Fields */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            background-color: #0d1117;
            color: white;
            border: 1px solid #30363D;
            border-radius: 8px;
        }
        
        /* DataFrame Styling */
        div[data-testid="stDataFrame"] {
            background-color: #1F2937;
            border-radius: 10px;
            padding: 10px;
        }
        
        /* Alerts */
        .stSuccess { background-color: rgba(21, 87, 36, 0.2); border: 1px solid #155724; color: #d4edda; }
        .stError { background-color: rgba(114, 28, 36, 0.2); border: 1px solid #721c24; color: #f8d7da; }
        .stInfo { background-color: rgba(12, 84, 96, 0.2); border: 1px solid #0c5460; color: #d1ecf1; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            category TEXT,
            status TEXT,
            borrower TEXT,
            date_issued TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on first run
init_db()

# --- 3. DATABASE FUNCTIONS ---
def add_book_to_db(book_id, title, author, category):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)', 
                  (book_id, title, author, category, 'Available', None, None))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # ID already exists
    finally:
        conn.close()

def get_all_books():
    conn = sqlite3.connect('library.db')
    # Use pandas to read sql easily
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df

def update_status(book_id, status, borrower=None, date=None):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET status=?, borrower=?, date_issued=? WHERE book_id=?", 
              (status, borrower, date, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE book_id=?", (book_id,))
    conn.commit()
    conn.close()

# --- 4. UI & NAVIGATION ---

# Sidebar
st.sidebar.title("📚 Library Menu")
menu = st.sidebar.radio("Go to:", ["Dashboard", "Add New Book", "Issue Book", "Return Book", "Search & Manage"])

# --- PAGE 1: DASHBOARD ---
if menu == "Dashboard":
    
    # --- HEADER: COLLEGE LOGO & NAME ---
    # Using columns to center the content
    # [10, 3, 10] ratio creates a narrow center column to force the logo to the middle
    col1, col2, col3 = st.columns([10, 3, 10])
    with col2:
        try:
            # Ensure 'logo.jpeg' is in the same directory
            st.image("logo.jpeg", use_container_width=True)
        except Exception:
            # Fallback if logo is missing
            st.warning("Logo not found (logo.jpeg)")
    
    st.markdown("<h2 style='text-align: center;'>BMS College of Engineering</h2>", unsafe_allow_html=True)
    st.markdown("---")
    # -----------------------------------

    st.title("📊 Library Dashboard")
    df = get_all_books()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        total_books = len(df)
        issued_books = len(df[df['status'] == 'Issued'])
        available_books = total_books - issued_books
        
        col1.metric("Total Books", total_books)
        col2.metric("Books Issued", issued_books, delta_color="inverse")
        col3.metric("Available Now", available_books)
        
        st.markdown("### 🆕 Recently Added Books")
        st.dataframe(df.tail(5), use_container_width=True)
    else:
        st.info("Library is empty. Go to 'Add New Book' to start.")

# --- PAGE 2: ADD BOOK ---
elif menu == "Add New Book":
    st.title("➕ Add New Book")
    with st.form("add_book_form"):
        c1, c2 = st.columns(2)
        b_id = c1.text_input("Book ID (Unique)", placeholder="e.g., BK001")
        b_cat = c2.selectbox("Category", ["Engineering", "Fiction", "Science", "History", "Business"])
        b_title = st.text_input("Book Title")
        b_author = st.text_input("Author Name")
        
        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if b_id and b_title:
                success = add_book_to_db(b_id, b_title, b_author, b_cat)
                if success:
                    st.success(f"✅ Book '{b_title}' added successfully!")
                else:
                    st.error("❌ Error: Book ID already exists.")
            else:
                st.warning("⚠️ Please fill in all fields.")

# --- PAGE 3: ISSUE BOOK ---
elif menu == "Issue Book":
    st.title("📤 Issue Book to Student")
    df = get_all_books()
    
    # Filter only available books
    available_books = df[df['status'] == 'Available']
    
    if available_books.empty:
        st.info("No books available to issue.")
    else:
        # Create a list of strings "ID - Title" for the dropdown
        book_options = available_books['book_id'] + " - " + available_books['title']
        selected_book = st.selectbox("Select Book to Issue", book_options)
        student_name = st.text_input("Student Name / USN")
        
        if st.button("Confirm Issue"):
            if student_name:
                # Extract Book ID from the selection string
                book_id_to_issue = selected_book.split(" - ")[0]
                date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                update_status(book_id_to_issue, 'Issued', student_name, date_now)
                st.success(f"✅ Book issued to {student_name}!")
                st.rerun() # Refresh page to update list
            else:
                st.error("Please enter Student Name.")

# --- PAGE 4: RETURN BOOK ---
elif menu == "Return Book":
    st.title("📥 Return Book")
    df = get_all_books()
    
    # Filter only issued books
    issued_books = df[df['status'] == 'Issued']
    
    if issued_books.empty:
        st.info("No books are currently issued out.")
    else:
        book_options = issued_books['book_id'] + " - " + issued_books['title'] + " (Borrowed by: " + issued_books['borrower'] + ")"
        selected_book = st.selectbox("Select Book to Return", book_options)
        
        if st.button("Process Return"):
            book_id_to_return = selected_book.split(" - ")[0]
            update_status(book_id_to_return, 'Available')
            st.success("✅ Book returned successfully!")
            st.rerun()

# --- PAGE 5: SEARCH & MANAGE ---
elif menu == "Search & Manage":
    st.title("🔍 Search & Manage Inventory")
    df = get_all_books()
    
    # Search Bar
    search_term = st.text_input("Search by Title, Author, or ID")
    
    if search_term:
        # Simple case-insensitive search across all columns
        mask = df.apply(lambda x: x.astype(str).str.contains(search_term, case=False).any(), axis=1)
        df_display = df[mask]
    else:
        df_display = df
        
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🗑️ Delete Book")
    del_id = st.text_input("Enter Book ID to Delete")
    if st.button("Delete Permanently", type="primary"):
        if del_id in df['book_id'].values:
            delete_book(del_id)
            st.warning(f"Book {del_id} deleted.")
            st.rerun()
        else:
            st.error("Book ID not found.")
