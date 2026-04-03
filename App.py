import streamlit as st
import random
import time

st.set_page_config(page_title="Snake Game", layout="centered")

# ==============================
# SETTINGS
# ==============================
GRID_SIZE = 20
GAME_SPEED = 0.2

st.title("🐍 Snake Game (Button Control)")

# ==============================
# SAFE INIT FUNCTION
# ==============================
def init_game():
    if "snake" not in st.session_state:
        st.session_state.snake = [(10, 10)]
    if "direction" not in st.session_state:
        st.session_state.direction = (0, 1)
    if "next_direction" not in st.session_state:
        st.session_state.next_direction = (0, 1)
    if "food" not in st.session_state:
        st.session_state.food = (
            random.randint(0, GRID_SIZE-1),
            random.randint(0, GRID_SIZE-1)
        )
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

init_game()

# ==============================
# 🎮 CONTROLS
# ==============================
st.markdown("### 🎮 Controls")

c1, c2, c3 = st.columns([1,1,1])
with c2:
    if st.button("⬆️ Up"):
        st.session_state.next_direction = (-1, 0)

c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("⬅️ Left"):
        st.session_state.next_direction = (0, -1)
with c3:
    if st.button("➡️ Right"):
        st.session_state.next_direction = (0, 1)

c1, c2, c3 = st.columns([1,1,1])
with c2:
    if st.button("⬇️ Down"):
        st.session_state.next_direction = (1, 0)

# ==============================
# SAFE DIRECTION UPDATE
# ==============================
dx, dy = st.session_state.direction
ndx, ndy = st.session_state.next_direction

# prevent reverse
if (dx, dy) != (-ndx, -ndy):
    st.session_state.direction = (ndx, ndy)

# ==============================
# GAME LOGIC
# ==============================
if not st.session_state.game_over:
    head = st.session_state.snake[0]
    dx, dy = st.session_state.direction

    new_head = (head[0] + dx, head[1] + dy)

    if (
        new_head[0] < 0 or new_head[0] >= GRID_SIZE or
        new_head[1] < 0 or new_head[1] >= GRID_SIZE or
        new_head in st.session_state.snake
    ):
        st.session_state.game_over = True
    else:
        st.session_state.snake.insert(0, new_head)

        if new_head == st.session_state.food:
            st.session_state.score += 1
            st.session_state.food = (
                random.randint(0, GRID_SIZE-1),
                random.randint(0, GRID_SIZE-1)
            )
        else:
            st.session_state.snake.pop()

# ==============================
# 🎨 DRAW GRID
# ==============================
grid_html = "<div style='display:inline-block; background:#111; padding:10px;'>"

for i in range(GRID_SIZE):
    row_html = "<div style='display:flex;'>"
    for j in range(GRID_SIZE):

        color = "#222"

        if (i, j) == st.session_state.food:
            color = "red"
        elif (i, j) == st.session_state.snake[0]:
            color = "#00ffcc"
        elif (i, j) in st.session_state.snake:
            color = "lime"

        row_html += f"""
        <div style="
            width:15px;
            height:15px;
            background:{color};
            margin:1px;
            border-radius:3px;
        "></div>
        """

    row_html += "</div>"
    grid_html += row_html

grid_html += "</div>"

st.markdown(grid_html, unsafe_allow_html=True)

# ==============================
# SCORE
# ==============================
st.subheader(f"🏆 Score: {st.session_state.score}")

# ==============================
# GAME OVER
# ==============================
if st.session_state.game_over:
    st.error("💀 Game Over!")

    if st.button("🔄 Restart Game"):
        st.session_state.clear()
        st.rerun()

# ==============================
# LOOP
# ==============================
time.sleep(GAME_SPEED)
st.rerun()
