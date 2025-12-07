export default class InputHandler {
    constructor() {
        this.keys = {};
        this.pressedKeys = {}; // Track single key presses
        this.mouse = { x: 0, y: 0, down: false };

        window.addEventListener('keydown', (e) => {
            if (!this.keys[e.code]) {
                this.pressedKeys[e.code] = true;
            }
            this.keys[e.code] = true;
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });

        window.addEventListener('mousemove', (e) => {
            const canvas = document.getElementById('gameCanvas');
            const rect = canvas.getBoundingClientRect();
            // Calculate scale in case canvas is resized via CSS
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            this.mouse.x = (e.clientX - rect.left) * scaleX;
            this.mouse.y = (e.clientY - rect.top) * scaleY;
        });

        window.addEventListener('mousedown', () => {
            this.mouse.down = true;
        });

        window.addEventListener('mouseup', () => {
            this.mouse.down = false;
        });
    }

    isKeyDown(code) {
        return !!this.keys[code];
    }

    isKeyPressed(code) {
        if (this.pressedKeys[code]) {
            this.pressedKeys[code] = false;
            return true;
        }
        return false;
    }

    getMousePos() {
        return { x: this.mouse.x, y: this.mouse.y };
    }
}
