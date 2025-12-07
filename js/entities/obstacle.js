import Entity from './entity.js';

export default class Obstacle extends Entity {
    constructor(x, y, width, height) {
        super(x, y, width, height, '#888'); // Grey color for walls
    }

    // Obstacles don't update or move
    update(deltaTime) { }
}
