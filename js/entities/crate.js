import Entity from './entity.js';
import { Utils } from '../utils.js';
import Weapon, { WeaponTypes } from './weapon.js';

export default class Crate extends Entity {
    constructor(game, x, y) {
        super(x, y, 30, 30, '#8B4513'); // Brown crate
        this.game = game;

        // Random weapon
        const types = Object.keys(WeaponTypes);
        this.weaponType = types[Math.floor(Math.random() * types.length)];
    }

    update(deltaTime) {
        // Check collision with characters
        for (const entity of this.game.entities) {
            if (entity.constructor.name === 'Character' && !entity.isDead) {
                if (Utils.rectIntersect(this.getBounds(), entity.getBounds())) {
                    this.pickup(entity);
                }
            }
        }
    }

    pickup(character) {
        character.weapon = new Weapon(this.game, character, this.weaponType);
        this.markedForDeletion = true;
        // Play sound or effect
        console.log(`${character.type} picked up ${this.weaponType}`);
    }
}
