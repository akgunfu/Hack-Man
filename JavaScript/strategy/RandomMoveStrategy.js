/**
 * This file is part of the Booking.com Hack-man JavaScript starter bot
 *
 * Last update: September 29, 2016
 *
 * @author Niko van Meurs <niko@riddles.io>
 * @License MIT License (http://opensource.org/Licenses/MIT)
 */
const logic = require('../logic');

/**
 * This class defines a strategy which returns a random but valid move.
 * Copy this class and replace the execute function to define your own.
 */
class RandomMoveStrategy {

    /**
     * Executes the RandomMoveStrategy
     *
     * @param {Object} gameSettings The bot's game settings
     * @param {Object} state        The state for which a move should be calculated (usually Bot.state)
     *
     * @returns {String} one of 'up', 'down', 'left', 'right' or 'pass'
     */
    execute(gameSettings, state) {
        const availableMoves = logic.getAvailableMoves(gameSettings, state);
        const randomIndex = Math.floor(Math.random() * availableMoves.length);

        return availableMoves[randomIndex];
    }
}

module.exports = RandomMoveStrategy;
