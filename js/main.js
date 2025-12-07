import Game from './game.js';

window.addEventListener('DOMContentLoaded', () => {
    const game = new Game();

    const startBtn = document.getElementById('start-btn');
    const shopUpgradeBtn = document.getElementById('shop-upgrade-btn');
    const shopCloseBtn = document.getElementById('shop-close-btn');
    const enemyCountDec = document.getElementById('enemy-count-dec');
    const enemyCountInc = document.getElementById('enemy-count-inc');
    const enemyCountValue = document.getElementById('enemy-count-value');

    startBtn.addEventListener('click', () => {
        game.enemyCount = parseInt(enemyCountValue.textContent);
        game.start();
    });

    shopUpgradeBtn.addEventListener('click', () => {
        game.handleShopPurchase();
    });

    shopCloseBtn.addEventListener('click', () => {
        game.toggleShop();
    });

    enemyCountDec.addEventListener('click', () => {
        let count = parseInt(enemyCountValue.textContent);
        if (count > 1) {
            count--;
            enemyCountValue.textContent = count;
        }
    });

    enemyCountInc.addEventListener('click', () => {
        let count = parseInt(enemyCountValue.textContent);
        if (count < 20) {
            count++;
            enemyCountValue.textContent = count;
        }
    });
});
