import Entity from './entity.js';
import { Utils } from '../utils.js';

export default class Projectile extends Entity {
    constructor(game, x, y, direction, speed, damage, range, owner) {
        super(x, y, 10, 10, '#ff0'); // Yellow bullets
        this.game = game;
        this.direction = direction;
        this.speed = speed;
        this.damage = damage;
        this.range = range;
        this.owner = owner; // 'player' or 'enemy'
        this.distanceTraveled = 0;
    }

    update(deltaTime) {
        const moveX = this.direction.x * this.speed * deltaTime;
        const moveY = this.direction.y * this.speed * deltaTime;

        this.x += moveX;
        this.y += moveY;

        this.distanceTraveled += Math.sqrt(moveX * moveX + moveY * moveY);

        if (this.distanceTraveled >= this.range) {
            this.markedForDeletion = true;
        }

        // Check collision with obstacles
        const bounds = this.getBounds();
        for (const obstacle of this.game.obstacles) {
            if (Utils.rectIntersect(bounds, obstacle.getBounds())) {
                this.markedForDeletion = true;
                return;
            }
        }

        // Check collision with characters
        for (const entity of this.game.entities) {
            // Skip if entity is the owner or not a character (e.g. obstacles are in entities list? No, obstacles are separate in game.obstacles but merged in game.entities for drawing/updating. Wait, game.entities includes obstacles. Need to check type.)
            // Actually, in game.js: this.entities = [this.player, this.enemy, ...this.obstacles];
            // So we need to check if entity is a Character and not the owner.

            if (entity === this.owner) continue;
            if (entity.constructor.name !== 'Character') continue; // Simple check

            if (Utils.rectIntersect(bounds, entity.getBounds())) {
                entity.takeDamage(this.damage);
                this.markedForDeletion = true;

                // Update score
                if (this.owner === this.game.player) {
                    this.game.updateScore('player', this.damage);
                } else {
                    this.game.updateScore('cpu', this.damage);
                }
                return;
            }
        }
    }
}
