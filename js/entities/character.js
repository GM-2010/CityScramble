import Entity from './entity.js';
import { Utils } from '../utils.js';
import Weapon from './weapon.js';

export default class Character extends Entity {
    constructor(game, x, y, type) {
        super(x, y, 40, 40, '#fff'); // Default size 40x40
        this.game = game;
        this.type = type;

        // Stats based on type
        this.stats = this.getStats(type);
        this.hp = 100; // Base HP
        this.maxHp = 100;
        this.speed = this.stats.speed;
        this.armor = this.stats.armor;

        this.velocity = { x: 0, y: 0 };
        this.direction = { x: 0, y: 1 }; // Facing down by default

        this.weapon = new Weapon(game, this, 'Pistol'); // Default weapon
        this.isDead = false;
        this.respawnTimer = 0;

        // Ability
        this.abilityCooldown = 0;
        this.abilityActive = false;
        this.abilityDuration = 0;
    }

    getStats(type) {
        switch (type) {
            case 'Flitzer': return { speed: 300, armor: 1.2 };
            case 'Tank': return { speed: 100, armor: 0.5 }; // Takes 50% damage
            case 'Allrounder': return { speed: 200, armor: 1.0 };
            case 'Jäger': return { speed: 250, armor: 1.1 };
            case 'Falle': return { speed: 200, armor: 1.0 };
            default: return { speed: 200, armor: 1.0 };
        }
    }

    update(deltaTime) {
        if (this.isDead) {
            this.respawnTimer -= deltaTime;
            if (this.respawnTimer <= 0) {
                this.respawn();
            }
            return;
        }

        this.handleMovement(deltaTime);
        this.handleAbility(deltaTime);

        // Update weapon if exists
        if (this.weapon) {
            this.weapon.update(deltaTime);
        }
    }

    handleMovement(deltaTime) {
        // To be overridden or controlled by Input/AI
    }

    move(inputVector, deltaTime) {
        if (inputVector.x !== 0 || inputVector.y !== 0) {
            // Normalize vector
            const length = Math.sqrt(inputVector.x * inputVector.x + inputVector.y * inputVector.y);
            inputVector.x /= length;
            inputVector.y /= length;

            this.direction = { ...inputVector };
        }

        // Move X
        let nextX = this.x + inputVector.x * this.speed * deltaTime;
        // Boundary Check X
        nextX = Utils.clamp(nextX, 0, this.game.canvas.width - this.width);

        // Collision Check X
        let collisionX = false;
        const rectX = { x: nextX, y: this.y, width: this.width, height: this.height };
        for (const obstacle of this.game.obstacles) {
            if (Utils.rectIntersect(rectX, obstacle.getBounds())) {
                collisionX = true;
                break;
            }
        }
        if (!collisionX) {
            this.x = nextX;
        }

        // Move Y
        let nextY = this.y + inputVector.y * this.speed * deltaTime;
        // Boundary Check Y
        nextY = Utils.clamp(nextY, 0, this.game.canvas.height - this.height);

        // Collision Check Y
        let collisionY = false;
        const rectY = { x: this.x, y: nextY, width: this.width, height: this.height };
        for (const obstacle of this.game.obstacles) {
            if (Utils.rectIntersect(rectY, obstacle.getBounds())) {
                collisionY = true;
                break;
            }
        }
        if (!collisionY) {
            this.y = nextY;
        }
    }

    handleAbility(deltaTime) {
        if (this.abilityCooldown > 0) this.abilityCooldown -= deltaTime;
        if (this.abilityDuration > 0) this.abilityDuration -= deltaTime;

        if (this.abilityDuration <= 0 && this.abilityActive) {
            this.deactivateAbility();
        }
    }

    activateAbility() {
        if (this.abilityCooldown > 0) return;

        // Implement specific ability logic here or in subclasses
        // For now, generic structure
        this.abilityActive = true;

        // Set cooldowns based on type
        switch (this.type) {
            case 'Flitzer':
                this.abilityDuration = 1;
                this.abilityCooldown = 15;
                break;
            case 'Tank':
                this.abilityDuration = 3;
                this.abilityCooldown = 20;
                break;
            // ... others
        }
    }

    deactivateAbility() {
        this.abilityActive = false;
    }

    attack() {
        if (this.weapon) {
            this.weapon.attack(this.direction);
        }
    }

    takeDamage(amount) {
        if (this.isDead) return;

        let actualDamage = amount * this.armor;

        // Special case for Tank ability
        if (this.type === 'Tank' && this.abilityActive) {
            actualDamage *= 0.5;
        }

        // Special case for Flitzer ability (Invulnerable)
        if (this.type === 'Flitzer' && this.abilityActive) {
            actualDamage = 0;
        }

        this.hp -= actualDamage;

        // Visual feedback
        if (this.game.spawnParticles) {
            this.game.spawnParticles(this.x + this.width / 2, this.y + this.height / 2, '#fff', 5);
        }

        if (this.hp <= 0) {
            this.die();
        }
    }

    die() {
        this.isDead = true;
        this.respawnTimer = 10;
        // Explosion of particles
        if (this.game.spawnParticles) {
            this.game.spawnParticles(this.x + this.width / 2, this.y + this.height / 2, this.color, 20);
        }
        this.x = -1000; // Move off screen
    }

    respawn() {
        this.isDead = false;
        this.hp = this.maxHp;
        this.x = 100; // Spawn point placeholder
        this.y = 100;
    }

    draw(ctx) {
        if (this.isDead) return;
        super.draw(ctx);

        // Draw direction indicator
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2, this.y + this.height / 2);
        ctx.lineTo(this.x + this.width / 2 + this.direction.x * 30, this.y + this.height / 2 + this.direction.y * 30);
        ctx.strokeStyle = 'red';
        ctx.stroke();
    }
}
