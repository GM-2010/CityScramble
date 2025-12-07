export default class Particle {
    constructor(game, x, y, color, speed, life) {
        this.game = game;
        this.x = x;
        this.y = y;
        this.color = color;
        this.life = life;
        this.maxLife = life;

        const angle = Math.random() * Math.PI * 2;
        this.velocity = {
            x: Math.cos(angle) * speed * Math.random(),
            y: Math.sin(angle) * speed * Math.random()
        };
        this.size = Math.random() * 3 + 2;
        this.markedForDeletion = false;
    }

    update(deltaTime) {
        this.x += this.velocity.x * deltaTime;
        this.y += this.velocity.y * deltaTime;

        this.life -= deltaTime;
        if (this.life <= 0) {
            this.markedForDeletion = true;
        }
    }

    draw(ctx) {
        ctx.globalAlpha = this.life / this.maxLife;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    }
}
