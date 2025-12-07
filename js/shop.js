export default class Shop {
    constructor(game) {
        this.game = game;
        this.upgradeTypes = ['fireRate', 'damage', 'quantity'];
        this.upgradeCost = 2000;
    }

    purchaseUpgrade() {
        // Check if player has enough score
        if (this.game.scores.player < this.upgradeCost) {
            return {
                success: false,
                message: 'Nicht genug Punkte! Du benötigst 2000 Punkte.'
            };
        }

        // Get player weapon
        if (!this.game.player || !this.game.player.weapon) {
            return {
                success: false,
                message: 'Keine Waffe verfügbar!'
            };
        }

        const weapon = this.game.player.weapon;

        // Select random upgrade type
        const upgradeType = this.upgradeTypes[Math.floor(Math.random() * this.upgradeTypes.length)];

        // Apply upgrade
        let upgradeName = '';
        let upgradeDescription = '';

        switch (upgradeType) {
            case 'fireRate':
                weapon.fireRateUpgrades++;
                upgradeName = 'Feuerrate';
                upgradeDescription = `Schießschnelligkeit um 0.1s verbessert (Stufe ${weapon.fireRateUpgrades})`;
                break;
            case 'damage':
                weapon.damageUpgrades++;
                upgradeName = 'Schaden';
                upgradeDescription = `Schaden um 10% erhöht (Stufe ${weapon.damageUpgrades})`;
                break;
            case 'quantity':
                weapon.quantityUpgrades++;
                upgradeName = 'Anzahl';
                upgradeDescription = `+1 zusätzliches Projektil (Stufe ${weapon.quantityUpgrades})`;
                break;
        }

        // Deduct cost
        this.game.updateScore('player', -this.upgradeCost);

        return {
            success: true,
            weaponName: weapon.config.name,
            upgradeName: upgradeName,
            upgradeDescription: upgradeDescription,
            remainingScore: this.game.scores.player
        };
    }
}
