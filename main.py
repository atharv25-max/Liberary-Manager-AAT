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

# --- CUSTOM CSS FOR MODERN DARK THEME ---
st.markdown("""
    <style>
        /* Global Settings */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Main Background */
        .stApp {
            background-color: #0F172A; /* Slate 900 */
            color: #E2E8F0; /* Slate 200 */
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1E293B; /* Slate 800 */
            border-right: 1px solid #334155;
        }
        
        /* Headings */
        h1 {
            background: linear-gradient(90deg, #60A5FA, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        h2, h3 {
            color: #F8FAFC !important;
            font-weight: 600;
        }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #1E293B; /* Slate 800 */
            border: 1px solid #334155;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #60A5FA;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }
        div[data-testid="stMetric"] label {
            color: #94A3B8; /* Slate 400 */
            font-size: 0.9rem;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px -1px rgba(59, 130, 246, 0.6);
        }
        
        /* Input Fields */
        .stTextInput > div > div > input {
            background-color: #1E293B;
            color: white;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 10px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #60A5FA;
            box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
        }
        
        /* Selectbox */
        .stSelectbox > div > div > div {
            background-color: #1E293B;
            color: white;
            border: 1px solid #475569;
            border-radius: 8px;
        }
        
        /* DataFrame */
        div[data-testid="stDataFrame"] {
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
        }
        
        /* Success/Error/Info Messages */
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34D399;
            border-radius: 8px;
        }
        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #F87171;
            border-radius: 8px;
        }
        .stInfo {
            background-color: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            color: #60A5FA;
            border-radius: 8px;
        }
        
        /* Custom horizontal rule */
        hr {
            margin: 2em 0;
            border: 0;
            border-top: 1px solid #334155;
        }
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
