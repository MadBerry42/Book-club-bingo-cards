#----------------------------- 1. Data storage (Supabase) ---------------------------------------
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

try:
    from dotenv import load_dotenv
    load_dotenv() # Loads the private credentials securily
except ImportError:
    pass

st.set_page_config(layout="wide", page_title="Book Club Bingo", page_icon="📚")


try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

if not url or not key:
    st.error("Missing Supabase credentials. Please check your .env file or Streamlit Secrets.")
    st.stop()

supabase: Client = create_client(url, key) #Interact with the supabase database

#------------------------ 2. Choosing the book: creating the book pile ------------------------
def get_book_pile():
    book_from_pile = supabase.table('books_pile').select('*').execute()
    return book_from_pile.data

def add_book_pile(title, book_pile):
    if title not in book_pile:
        supabase.table('books_pile').insert({'title': title}).execute()
    else:
        st.error("Book already on the shelf!")

# Artwork: Use HTML/CSS to select the style for different parts of the window
st.markdown("""
<style>
    .book_pile div.stButton > button {
        width: 100%;
        border-left: 12px solid #5c3a21 !important; /* Dorso del libro */
        border-radius: 4px 12px 12px 4px !important;
        padding: 15px 10px !important;
        text-align: left !important;
        font-weight: bold !important;
        background-color: #4a7c59 !important; /* Colore copertina di default */
        color: white !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.15) !important;
        margin-bottom: 8px !important;
        transition: transform 0.2s ease;
    }
    
    /* Move book when hovering over it */
    .book_pile div.stButton > button:hover {
        transform: translateX(-5px);
        background-color: #689f74 !important;
    }

</style>
""", unsafe_allow_html=True)

if "libro_attivo" not in st.session_state:
    st.session_state.libro_attivo = None

def remove_book(title):
    supabase.table('books_pile').delete().eq({'title': title}).execute()

#--------------------------------  3. Bingo cards ------------------------------------------------
def get_cards_for_book(title): # Function that retrieves all the tasks from the todo database
    response = supabase.table('cards').select('*').eq('title').execute()  # select('*') = select all columns and execute the query
    return response.data #results of the query, contains all the columns in the table

def add_card(card): # Add a task to the list
    supabase.table('cards').insert({
        'card': card}).execute()

st.title("Bingo card list")

# -------------------------------- 4. UI interface details -----------------------------------
col_cards, col_book_pile = st.columns([0.7, 0.3])

# ---------------------------- 5. Add books to the pile --------------------------------------
book_pile = get_book_pile()
with col_book_pile:    
    with st.popover("Add a book"):
        new_book = st.text_input("Title: ")
        confirm_button = st.button("Add")

        if confirm_button:
            if new_book.strip():
                if add_book_pile(new_book, book_pile):
                    st.session_state.libro_attivo = new_book
                    st.rerun()

    with st.container(border=False):
        st.markdown('<div class="book_pile">', unsafe_allow_html=True)
        for book in reversed(book_pile):
            book_title = book['title']
            book_id = book['id']

            label = f"📖 {book_title}"
            if st.button(label, key=f"btn_{book_id}"):
                st.session_state.libro_attivo = book
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)



        
        

