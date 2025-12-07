import InputHandler from './input.js';
import Character from './entities/character.js';
import Obstacle from './entities/obstacle.js';
import AIController from './ai/aiController.js';
import Crate from './entities/crate.js';
import Particle from './entities/particle.js';
import Shop from './shop.js';

export default class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Set canvas size to match CSS size (internal resolution)
        this.canvas.width = 1280;
        this.canvas.height = 720;

        this.lastTime = 0;
        this.isRunning = false;
        this.isGameOver = false;

        // UI Elements
        this.startScreen = document.getElementById('start-screen');
        this.gameOverScreen = document.getElementById('game-over-screen');
        this.shopScreen = document.getElementById('shop-screen');
        this.hud = document.getElementById('hud');
        this.timerDisplay = document.getElementById('timer');

        // Game State
        this.gameTime = 180; // 3 minutes in seconds
        this.entities = [];
        this.projectiles = [];
        this.particles = [];
        this.player = null;
        this.enemy = null;
        this.aiController = null;
        this.input = new InputHandler();
        this.shop = new Shop(this);
        this.isShopOpen = false;

        this.crateSpawnTimer = 0;

        // Enemy count setting
        this.enemyCount = 1;

        // Persistent score system
        this.totalScore = this.loadTotalScore();
        this.updateTotalScoreDisplay();
    }

    start() {
        this.startScreen.classList.add('hidden');
        this.hud.classList.remove('hidden');
        this.isRunning = true;
        this.isGameOver = false;
        this.gameTime = 180;
        this.lastTime = performance.now();

        // Initialize entities
        this.player = new Character(this, 100, 100, 'Flitzer'); // Player is Flitzer

        // Create multiple enemies based on enemy count setting
        this.enemies = [];
        for (let i = 0; i < this.enemyCount; i++) {
            const x = 800 + (i % 3) * 200; // Spread enemies horizontally
            const y = 200 + Math.floor(i / 3) * 200; // Spread enemies vertically
            const enemy = new Character(this, x, y, 'Tank');
            enemy.color = '#f00';
            this.enemies.push(enemy);
        }

        // For backwards compatibility, keep this.enemy as the first enemy
        this.enemy = this.enemies[0];

        this.aiController = new AIController(this, this.enemy);

        this.obstacles = [
            new Obstacle(300, 200, 100, 300),
            new Obstacle(600, 100, 400, 50),
            new Obstacle(800, 400, 50, 200),
            new Obstacle(200, 500, 200, 50)
        ];

        this.entities = [this.player, ...this.enemies, ...this.obstacles];
        this.projectiles = [];
        this.particles = [];

        this.scores = { player: 0, cpu: 0 };
        this.updateScoreDisplay();

        this.crateSpawnTimer = 10; // First crate after 10s

        requestAnimationFrame((ts) => this.loop(ts));
    }

    restart() {
        this.gameOverScreen.classList.add('hidden');
        this.start();
    }

    loop(timestamp) {
        if (!this.isRunning) return;

        const deltaTime = (timestamp - this.lastTime) / 1000;
        this.lastTime = timestamp;

        this.update(deltaTime);
        this.draw();

        if (!this.isGameOver) {
            requestAnimationFrame((ts) => this.loop(ts));
        }
    }

    update(deltaTime) {
        // Update Timer
        this.gameTime -= deltaTime;
        if (this.gameTime <= 0) {
            this.gameTime = 0;
            this.endGame();
        }
        this.updateTimerDisplay();

        // Crate Spawning
        this.crateSpawnTimer -= deltaTime;
        if (this.crateSpawnTimer <= 0) {
            this.spawnCrate();
            this.crateSpawnTimer = 15; // Spawn every 15s
        }

        // Player Input
        if (this.player && !this.player.isDead) {
            const inputVector = { x: 0, y: 0 };
            if (this.input.isKeyDown('KeyW') || this.input.isKeyDown('ArrowUp')) inputVector.y -= 1;
            if (this.input.isKeyDown('KeyS') || this.input.isKeyDown('ArrowDown')) inputVector.y += 1;
            if (this.input.isKeyDown('KeyA') || this.input.isKeyDown('ArrowLeft')) inputVector.x -= 1;
            if (this.input.isKeyDown('KeyD') || this.input.isKeyDown('ArrowRight')) inputVector.x += 1;

            this.player.move(inputVector, deltaTime);

            if (this.input.isKeyDown('KeyQ')) {
                this.player.activateAbility();
            }

            if (this.input.isKeyDown('Space')) {
                this.player.attack();
            }

            // Toggle shop with E key
            if (this.input.isKeyPressed('KeyE')) {
                this.toggleShop();
            }
        }

        // AI Update
        if (this.aiController) {
            this.aiController.update(deltaTime);
        }

        // Update Entities
        this.entities.forEach(e => e.update(deltaTime));
        this.entities = this.entities.filter(e => !e.markedForDeletion);

        // Update Projectiles
        this.projectiles.forEach(p => p.update(deltaTime));
        this.projectiles = this.projectiles.filter(p => !p.markedForDeletion);

        // Update Particles
        this.particles.forEach(p => p.update(deltaTime));
        this.particles = this.particles.filter(p => !p.markedForDeletion);

        // Update HUD Bars
        this.updateHUD();
    }

    draw() {
        // Clear screen
        this.ctx.fillStyle = '#444'; // Placeholder background
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw Entities
        this.entities.forEach(e => e.draw(this.ctx));

        // Draw Projectiles
        this.projectiles.forEach(p => p.draw(this.ctx));

        // Draw Particles
        this.particles.forEach(p => p.draw(this.ctx));
    }

    spawnCrate() {
        const x = Math.random() * (this.canvas.width - 100) + 50;
        const y = Math.random() * (this.canvas.height - 100) + 50;
        const crate = new Crate(this, x, y);
        this.entities.push(crate);
    }

    spawnParticles(x, y, color, count) {
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(this, x, y, color, 100, 0.5));
        }
    }

    addProjectile(projectile) {
        this.projectiles.push(projectile);
    }

    updateScore(who, amount) {
        this.scores[who] += amount;
        this.updateScoreDisplay();
    }

    updateScoreDisplay() {
        document.getElementById('p1-score').textContent = Math.floor(this.scores.player);
        document.getElementById('cpu-score').textContent = Math.floor(this.scores.cpu);
    }

    updateHUD() {
        if (this.player) {
            const hpPercent = Math.max(0, (this.player.hp / this.player.maxHp) * 100);
            document.getElementById('hp-bar').style.width = `${hpPercent}%`;

            const abilityIcon = document.getElementById('ability-icon');
            if (this.player.abilityCooldown <= 0) {
                abilityIcon.classList.add('cooldown-ready');
                abilityIcon.style.opacity = 1;
            } else {
                abilityIcon.classList.remove('cooldown-ready');
                abilityIcon.style.opacity = 0.5;
            }

            // Ammo display
            const ammoDisplay = document.getElementById('ammo-display');
            if (this.player.weapon) {
                const ammo = this.player.weapon.config.ammo === Infinity ? 'Unendlich' : this.player.weapon.currentAmmo;
                ammoDisplay.textContent = ammo;
            }
        }
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.gameTime / 60);
        const seconds = Math.floor(this.gameTime % 60);
        this.timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    endGame() {
        this.isRunning = false;
        this.isGameOver = true;
        this.hud.classList.add('hidden');
        this.gameOverScreen.classList.remove('hidden');

        // Add current score to total score
        const earnedPoints = Math.floor(this.scores.player);
        this.totalScore += earnedPoints;
        this.saveTotalScore();

        document.getElementById('final-p1-score').textContent = earnedPoints;
        document.getElementById('final-cpu-score').textContent = Math.floor(this.scores.cpu);

        let winnerText = "Unentschieden!";
        if (this.scores.player > this.scores.cpu) winnerText = "Du hast gewonnen!";
        else if (this.scores.cpu > this.scores.player) winnerText = "CPU hat gewonnen!";

        document.getElementById('winner-text').textContent = winnerText;

        // Return to start screen after 3 seconds
        setTimeout(() => {
            this.returnToStart();
        }, 3000);
    }

    toggleShop() {
        if (this.isGameOver) return; // Don't open shop if game is over

        this.isShopOpen = !this.isShopOpen;

        if (this.isShopOpen) {
            this.shopScreen.classList.remove('hidden');
            // Update shop score display
            document.getElementById('shop-score').textContent = Math.floor(this.scores.player);
            // Clear previous message
            const shopMessage = document.getElementById('shop-message');
            shopMessage.textContent = '';
            shopMessage.className = '';
        } else {
            this.shopScreen.classList.add('hidden');
        }
    }

    handleShopPurchase() {
        const result = this.shop.purchaseUpgrade();
        const shopMessage = document.getElementById('shop-message');

        if (result.success) {
            shopMessage.className = 'success';
            shopMessage.innerHTML = `
                <strong>Upgrade erfolgreich!</strong><br>
                Waffe: ${result.weaponName}<br>
                Upgrade: ${result.upgradeName}<br>
                ${result.upgradeDescription}
            `;
            // Update score display
            document.getElementById('shop-score').textContent = Math.floor(result.remainingScore);
            this.updateScoreDisplay();
        } else {
            shopMessage.className = 'error';
            shopMessage.textContent = result.message;
        }
    }

    loadTotalScore() {
        const saved = localStorage.getItem('cityScrambleTotalScore');
        return saved ? parseInt(saved, 10) : 0;
    }

    saveTotalScore() {
        localStorage.setItem('cityScrambleTotalScore', this.totalScore.toString());
        this.updateTotalScoreDisplay();
    }

    updateTotalScoreDisplay() {
        const totalScoreElement = document.getElementById('total-score');
        if (totalScoreElement) {
            totalScoreElement.textContent = this.totalScore.toLocaleString('de-DE');
        }
    }

    returnToStart() {
        this.gameOverScreen.classList.add('hidden');
        this.startScreen.classList.remove('hidden');
        this.updateTotalScoreDisplay();
    }
}
