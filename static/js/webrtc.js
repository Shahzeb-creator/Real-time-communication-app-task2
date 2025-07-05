const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
let drawing = false;

canvas.addEventListener("mousedown", () => drawing = true);
canvas.addEventListener("mouseup", () => drawing = false);
canvas.addEventListener("mouseout", () => drawing = false);

canvas.addEventListener("mousemove", e => {
    if (!drawing) return;
    const x = e.offsetX;
    const y = e.offsetY;
    draw(x, y);
    socket.emit("draw", { room, x, y });
});

socket.on("draw", ({ x, y }) => {
    draw(x, y);
});

function draw(x, y) {
    ctx.fillStyle = "#000";
    ctx.beginPath();
    ctx.arc(x, y, 2, 0, Math.PI * 2);
    ctx.fill();
}