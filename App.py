import streamlit as st
import streamlit.components.v1 as components
import random
import time

st.set_page_config(page_title="Snake Game", layout="centered")

# ==============================
# SETTINGS
# ==============================
GRID_SIZE = 20
GAME_SPEED = 0.25

st.title("🐍 Snake Game (Button Controlled)")

# ==============================
# SAFE INITIALIZATION
# ==============================
def init():
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

init()

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
# APPLY DIRECTION
# ==============================
dx, dy = st.session_state.direction
ndx, ndy = st.session_state.next_direction

# prevent reverse movement
if (dx, dy) != (-ndx, -ndy):
    st.session_state.direction = (ndx, ndy)

# ==============================
# GAME LOGIC
# ==============================
if not st.session_state.game_over:
    head = st.session_state.snake[0]
    dx, dy = st.session_state.direction

    new_head = (head[0] + dx, head[1] + dy)

    # collision
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
# 🎨 DRAW GRID (FIXED GRAPHICS)
# ==============================
grid_html = "<div style='display:inline-block; background:#111; padding:10px;'>"

for i in range(GRID_SIZE):
    grid_html += "<div style='display:flex;'>"
    for j in range(GRID_SIZE):

        color = "#222"

        if (i, j) == st.session_state.food:
            color = "red"
        elif (i, j) == st.session_state.snake[0]:
            color = "#00ffcc"
        elif (i, j) in st.session_state.snake:
            color = "lime"

        grid_html += f"""
        <div style="
            width:15px;
            height:15px;
            background:{color};
            margin:1px;
            border-radius:3px;
        "></div>
        """

    grid_html += "</div>"

grid_html += "</div>"

# ✅ KEY FIX: render with components
components.html(grid_html, height=500)

# ==============================
# SCORE
# ==============================
st.subheader(f"🏆 Score: {st.session_state.score}")

# ==============================
# GAME OVER
# ==============================
if st.session_state.game_over:
    st.error("💀 Game Over!")

    if st.button("🔄 Restart"):
        st.session_state.clear()
        st.rerun()

# ==============================
# GAME LOOP
# ==============================
time.sleep(GAME_SPEED)
st.rerun()
