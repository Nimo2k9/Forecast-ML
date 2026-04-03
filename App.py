import streamlit as st
import random
import time
from streamlit_js_eval import streamlit_js_eval

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Snake Game", layout="centered")

st.title("🐍 Snake Game (Streamlit)")

# ==============================
# GAME SETTINGS
# ==============================
GRID_SIZE = 20
WIDTH = 400
HEIGHT = 400

# ==============================
# SESSION STATE INIT
# ==============================
if "snake" not in st.session_state:
    st.session_state.snake = [(10, 10)]
    st.session_state.direction = (0, 1)
    st.session_state.food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
    st.session_state.score = 0
    st.session_state.game_over = False

# ==============================
# KEYBOARD INPUT
# ==============================
key = streamlit_js_eval(js_expressions="window.keyPressed", key="key")

if key:
    if key == "ArrowUp" and st.session_state.direction != (1, 0):
        st.session_state.direction = (-1, 0)
    elif key == "ArrowDown" and st.session_state.direction != (-1, 0):
        st.session_state.direction = (1, 0)
    elif key == "ArrowLeft" and st.session_state.direction != (0, 1):
        st.session_state.direction = (0, -1)
    elif key == "ArrowRight" and st.session_state.direction != (0, -1):
        st.session_state.direction = (0, 1)

# ==============================
# GAME LOOP
# ==============================
if not st.session_state.game_over:
    head = st.session_state.snake[0]
    dx, dy = st.session_state.direction
    new_head = (head[0] + dx, head[1] + dy)

    # Wall collision
    if (
        new_head[0] < 0 or new_head[0] >= GRID_SIZE or
        new_head[1] < 0 or new_head[1] >= GRID_SIZE or
        new_head in st.session_state.snake
    ):
        st.session_state.game_over = True

    else:
        st.session_state.snake.insert(0, new_head)

        # Food eaten
        if new_head == st.session_state.food:
            st.session_state.score += 1
            st.session_state.food = (
                random.randint(0, GRID_SIZE-1),
                random.randint(0, GRID_SIZE-1)
            )
        else:
            st.session_state.snake.pop()

# ==============================
# DRAW GRID
# ==============================
grid = [["⬛" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Draw food
fx, fy = st.session_state.food
grid[fx][fy] = "🍎"

# Draw snake
for x, y in st.session_state.snake:
    grid[x][y] = "🟩"

# Render grid
for row in grid:
    st.write("".join(row))

# ==============================
# SCORE
# ==============================
st.subheader(f"Score: {st.session_state.score}")

# ==============================
# GAME OVER
# ==============================
if st.session_state.game_over:
    st.error("💀 Game Over!")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()

# ==============================
# AUTO REFRESH (GAME SPEED)
# ==============================
time.sleep(0.2)
st.rerun()
