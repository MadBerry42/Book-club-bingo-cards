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
        response = supabase.table('books_pile').insert({'title': title}).execute()
        return response.data[0] if response.data else None
    else:
        st.error("Book already on the shelf!")
        return None

# -------- 3. Artwork: Use HTML/CSS to select the style for different parts of the window--------
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
            
    .corkboard {
        position: relative;
        width: 100%;
        height: 600px;
        background-color: #b87333;
        border-radius: 8px;
        box-shadow: inset 0px 4px 10px rgba(0, 0, 0, 0, 2);
        overflow: hidden;
    }
            
    .post-it {
            position: absolute;
            width: 140px;
            min-height: 140px;
            padding: 12px;
            box-shadow: 3px 3px 8px rgba(0, 0, 0, 0, 0.3);
            border-radius: 2px;
            transition: transform 0.15s linear;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            font-family: 'Courier New';
            font-size: 14px;
            color: #333;
            line-height: 1.2;
            word-wrap: break-word;
            transform: rotate(-1deg);
    }
            
    .post-it-text{
        font-size: 16px;
            font-weight: bold;
            line-height: 1.3;
            word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

postit_colors = {
    "🟡 Yellow": "#fef5c1",
    "💗 Pink": "#ffcce6",
    "🔵 Light blue": "#d0e8f2",
    "🟢 Green": "#dbf3c9",
    "🟣 Purple": "#e8d7f1"
}

if "active_book" not in st.session_state:
    st.session_state.active_book = None

def remove_book(title):
    supabase.table('books_pile').delete().eq('title', title).execute()

#--------------------------------  3. Bingo cards ------------------------------------------------
def get_cards_for_book(title): # Function that retrieves all the tasks from the todo database
    response = supabase.table('cards').select('*').eq('title', title).execute()  # select('*') = select all columns and execute the query
    return response.data #results of the query, contains all the columns in the table

def add_card(card, title, color): # Add a task to the list
    supabase.table('cards').insert({
        'card': card,
        'title': title,
        'color': color,
        'x_pos': 40,
        'y_pos': 40
        }).execute()
    
def update_card_position(card_id, x, y):
    supabase.table('cards').update({'x_pos': x, 'y_pos':y}).eq('id', card_id).execute()

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
                created_book = add_book_pile(new_book, book_pile)
                if created_book:
                    st.session_state.active_book = created_book
                    st.rerun()

    with st.container(border=False):
        st.markdown('<div class="book_pile">', unsafe_allow_html=True)
        for book in reversed(book_pile):
            book_title = book['title']
            book_id = book['id']

            label = f"📖 {book_title}"
            if st.button(label, key=f"btn_{book_id}"):
                st.session_state.active_book = book
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
if st.session_state.active_book:
    book_selected = st.session_state.active_book

    with st.popover("Place your post-it"):
        new_card = st.text_input(" ")
        color_choice = st.selectbox("Color: ", list(postit_colors.keys()))

        confirm_card = st.button("Appiccica sul muro!")
        if confirm_card and new_card.strip():
            colore_hex = postit_colors[color_choice]
            add_card(new_card, book_selected['title'], colore_hex)
            st.rerun()

with col_cards:
    if st.session_state.active_book:
        book = st.session_state.active_book
        book_title = book['title'] if isinstance(book, dict) else book

        st.subheader(f"{book_title}")
        
        cards_list = get_cards_for_book(book_title)
        
        html_corkboard = '<div class="corkboard">'
        
        for card in cards_list:
            # Recuperiamo dati dal DB (con valori di fallback se vuoti)
            colore = card.get('color', '#fef5c1')
            x = card.get('x_pos', 40)
            y = card.get('y_pos', 40)
            testo = card['card']
            
            # Posizioniamo il post-it usando top% e left% in base alle sue coordinate
            html_corkboard += f"""
            <div class="post-it" style="background-color: {colore}; left: {x}%; top: {y}%;">
                {testo}
            </div>
            """
        html_corkboard += '</div>'
        
        # Mostriamo la bacheca grafica
        st.markdown(html_corkboard, unsafe_allow_html=True)
        
        # --------------------------------------------- Moving the sticky notes --------------------------------------------------
        st.write("")
        with st.expander("(Re)move post-its"):
            if not cards_list:
                st.write("No post-it on the board")
            for card in cards_list:
                # Creiamo una riga per ogni post-it per poterlo regolare
                c_testo, c_x, c_y, c_del = st.columns([0.4, 0.25, 0.25, 0.1])
                
                c_testo.write(f"*{card['card']}*")
                
                new_x = c_x.slider("Horizontal (X)", 0, 85, int(card.get('x_pos', 40)), key=f"x_{card['id']}")
                new_y = c_y.slider("Vertical (Y)", 0, 75, int(card.get('y_pos', 40)), key=f"y_{card['id']}")
                
        
                if new_x != card.get('x_pos') or new_y != card.get('y_pos'):
                    update_card_position(card['id'], new_x, new_y)
                    st.rerun()
                
                if c_del.button("🗑️", key=f"del_{card['id']}"):
                    supabase.table('cards').delete().eq('id', card['id']).execute()
                    st.rerun()
                    
    else:
        st.info("👈 Seleziona a book from the pile!")
        
        

