import { Utils } from '../utils.js';

export default class AIController {
    constructor(game, character) {
        this.game = game;
        this.character = character;
        this.state = 'IDLE'; // IDLE, CHASE, ATTACK, FLEE
        this.target = null;
        this.updateTimer = 0;
    }

    update(deltaTime) {
        if (this.character.isDead) return;

        this.updateTimer -= deltaTime;
        if (this.updateTimer <= 0) {
            this.decideState();
            this.updateTimer = 0.5; // Re-evaluate every 0.5s
        }

        this.executeState(deltaTime);
    }

    decideState() {
        // Find target (Player)
        this.target = this.game.player;
        if (!this.target || this.target.isDead) {
            this.state = 'IDLE';
            return;
        }

        const dist = Utils.distance(this.character.x, this.character.y, this.target.x, this.target.y);

        // Simple logic based on health and distance
        if (this.character.hp < 30) {
            this.state = 'FLEE';
        } else if (dist < 300) { // Attack range (approx)
            this.state = 'ATTACK';
        } else {
            this.state = 'CHASE';
        }
    }

    executeState(deltaTime) {
        if (!this.target) return;

        const dx = this.target.x - this.character.x;
        const dy = this.target.y - this.character.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        const dir = { x: dx / dist, y: dy / dist };

        switch (this.state) {
            case 'IDLE':
                // Do nothing or wander
                this.character.move({ x: 0, y: 0 }, deltaTime);
                break;
            case 'CHASE':
                this.character.move(dir, deltaTime);
                break;
            case 'ATTACK':
                // Stop moving to shoot? Or strafe?
                // For now, stop and shoot
                this.character.move({ x: 0, y: 0 }, deltaTime);

                // Face target
                this.character.direction = dir;
                this.character.attack();
                break;
            case 'FLEE':
                this.character.move({ x: -dir.x, y: -dir.y }, deltaTime);
                break;
        }
    }
}
