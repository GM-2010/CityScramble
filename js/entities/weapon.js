import Projectile from './projectile.js';

export const WeaponTypes = {
    BaseballBat: { name: 'Baseballschläger', type: 'melee', damage: 10, cooldown: 0.5, ammo: Infinity, range: 60 },
    Pistol: { name: 'Pistole', type: 'ranged', damage: 20, cooldown: 0.8, ammo: 8, speed: 600, range: 400 },
    Shotgun: { name: 'Schrotflinte', type: 'ranged', damage: 35, cooldown: 2.0, ammo: 4, speed: 500, range: 300, spread: 3 },
    Boomerang: { name: 'Bumerang', type: 'thrown', damage: 15, cooldown: 1.5, ammo: 3, speed: 400, range: 300 },
    PoisonFlask: { name: 'Giftflasche', type: 'area', damage: 5, cooldown: 3.0, ammo: 2, speed: 300, range: 200 }, // Simplified
    Bomb: { name: 'Explosionsbombe', type: 'area', damage: 50, cooldown: 4.0, ammo: 1, speed: 0, range: 0 } // Simplified
};

export default class Weapon {
    constructor(game, owner, typeName) {
        this.game = game;
        this.owner = owner;
        this.config = WeaponTypes[typeName];
        this.currentAmmo = this.config.ammo;
        this.cooldownTimer = 0;

        // Upgrade tracking
        this.fireRateUpgrades = 0;
        this.damageUpgrades = 0;
        this.quantityUpgrades = 0;
    }

    update(deltaTime) {
        if (this.cooldownTimer > 0) {
            this.cooldownTimer -= deltaTime;
        }
    }

    attack(direction) {
        if (this.cooldownTimer > 0) return;
        if (this.currentAmmo <= 0 && this.config.ammo !== Infinity) return; // Out of ammo

        this.currentAmmo--;
        // Apply fire rate upgrades (-0.1s per upgrade)
        this.cooldownTimer = Math.max(0.1, this.config.cooldown - (this.fireRateUpgrades * 0.1));

        // Apply Allrounder ability (Cooldown reduction)
        if (this.owner.type === 'Allrounder' && this.owner.abilityActive) {
            this.cooldownTimer *= 0.5;
        }

        // Apply Jäger ability (Range/Speed boost) - pass to projectile
        let speed = this.config.speed;
        let range = this.config.range;
        if (this.owner.type === 'Jäger' && this.owner.abilityActive) {
            speed *= 1.2; // Not exactly "Geschossgeschwindigkeit" but close enough
            range *= 1.2;
        }

        // Apply damage upgrades (+10% per upgrade)
        let damage = this.config.damage * Math.pow(1.1, this.damageUpgrades);

        if (this.config.type === 'ranged') {
            if (this.config.name === 'Schrotflinte') {
                // Spread logic with quantity upgrades
                const baseProjectiles = 3; // Default 3 projectiles (-1, 0, 1)
                const totalProjectiles = baseProjectiles + this.quantityUpgrades;
                const spread = (totalProjectiles - 1) / 2;

                for (let i = -spread; i <= spread; i++) {
                    // Rotate direction slightly
                    const angle = Math.atan2(direction.y, direction.x) + i * 0.2;
                    const dir = { x: Math.cos(angle), y: Math.sin(angle) };
                    this.game.addProjectile(new Projectile(this.game, this.owner.x + this.owner.width / 2, this.owner.y + this.owner.height / 2, dir, speed, damage, range, this.owner));
                }
            } else {
                // Regular ranged weapons with quantity upgrades
                const projectileCount = 1 + this.quantityUpgrades;
                for (let i = 0; i < projectileCount; i++) {
                    // Slight spread for multiple projectiles
                    let dir = { ...direction };
                    if (projectileCount > 1) {
                        const spreadAngle = ((i - (projectileCount - 1) / 2) * 0.15);
                        const angle = Math.atan2(direction.y, direction.x) + spreadAngle;
                        dir = { x: Math.cos(angle), y: Math.sin(angle) };
                    }
                    this.game.addProjectile(new Projectile(this.game, this.owner.x + this.owner.width / 2, this.owner.y + this.owner.height / 2, dir, speed, damage, range, this.owner));
                }
            }
        } else if (this.config.type === 'melee') {
            // Melee logic (Hitbox check in front)
            // For now, just log it or create a short-lived invisible projectile
            console.log("Melee attack");
            // TODO: Implement Melee Hitbox
        }
    }
}
