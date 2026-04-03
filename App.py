import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Snake Game", layout="centered")

st.title("🐍 Snake Game (Graphics Version)")

html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    text-align: center;
    background-color: #111;
    color: white;
}
canvas {
    background-color: black;
    border: 3px solid #00ffcc;
}
</style>
</head>
<body>

<h3>Use Arrow Keys ⬅️➡️⬆️⬇️</h3>
<canvas id="game" width="400" height="400"></canvas>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const grid = 20;
let count = 0;

let snake = {
    x: 160,
    y: 160,
    dx: grid,
    dy: 0,
    cells: [],
    maxCells: 4
};

let apple = {
    x: 320,
    y: 320
};

let score = 0;

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

document.addEventListener("keydown", function(e) {
    if (e.key === "ArrowLeft" && snake.dx === 0) {
        snake.dx = -grid;
        snake.dy = 0;
    } else if (e.key === "ArrowUp" && snake.dy === 0) {
        snake.dy = -grid;
        snake.dx = 0;
    } else if (e.key === "ArrowRight" && snake.dx === 0) {
        snake.dx = grid;
        snake.dy = 0;
    } else if (e.key === "ArrowDown" && snake.dy === 0) {
        snake.dy = grid;
        snake.dx = 0;
    }
});

function gameLoop() {
    requestAnimationFrame(gameLoop);

    if (++count < 5) return;
    count = 0;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    snake.x += snake.dx;
    snake.y += snake.dy;

    // wall wrap
    if (snake.x < 0) snake.x = canvas.width - grid;
    else if (snake.x >= canvas.width) snake.x = 0;

    if (snake.y < 0) snake.y = canvas.height - grid;
    else if (snake.y >= canvas.height) snake.y = 0;

    snake.cells.unshift({x: snake.x, y: snake.y});

    if (snake.cells.length > snake.maxCells) {
        snake.cells.pop();
    }

    // draw apple
    ctx.fillStyle = "red";
    ctx.fillRect(apple.x, apple.y, grid-1, grid-1);

    // draw snake
    ctx.fillStyle = "lime";
    snake.cells.forEach(function(cell, index) {
        ctx.fillRect(cell.x, cell.y, grid-1, grid-1);

        // eat apple
        if (cell.x === apple.x && cell.y === apple.y) {
            snake.maxCells++;
            score++;

            apple.x = getRandomInt(0, 20) * grid;
            apple.y = getRandomInt(0, 20) * grid;
        }

        // collision with self
        for (let i = index + 1; i < snake.cells.length; i++) {
            if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
                alert("Game Over! Score: " + score);
                snake.x = 160;
                snake.y = 160;
                snake.cells = [];
                snake.maxCells = 4;
                snake.dx = grid;
                snake.dy = 0;
                score = 0;
            }
        }
    });

    // score text
    ctx.fillStyle = "white";
    ctx.font = "16px Arial";
    ctx.fillText("Score: " + score, 10, 20);
}

requestAnimationFrame(gameLoop);
</script>

</body>
</html>
"""

components.html(html_code, height=500)
