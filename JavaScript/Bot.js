/**
 * This file is part of the Booking.com Hack-man JavaScript starter bot
 *
 * Last update: September 29, 2016
 *
 * @author Niko van Meurs <niko@riddles.io>
 * @License MIT License (http://opensource.org/Licenses/MIT)
 */
const readline = require('readline');
const utils = require('./utils');
const RandomMoveStrategy = require('./strategy/RandomMoveStrategy');

/**
 * This is the Bot's main class, everything you need to get started can
 * be found here.
 */
class Bot {

    constructor() {
        // An empty object in which we'll store the game settings
        // passed by the engine at the beginning of the game
        this.gameSettings = {
            timebank: null,
            time_per_move: null,
            player_names: null,
            your_bot: null,
            your_botid: null,
            field_width: null,
            field_height: null,
            max_rounds: null,
        };

        // An empty object which will store the game state
        this.state = {
            field: null,
            round: 0,
            players: {},
        };

        // The strategy executed by the bot when it is asked to provide
        // a move. Replace this with your own.
        this.strategy = new RandomMoveStrategy();
    }

    /**
     * Attaches the necessary events to the readline interface in order
     * to start the loop.
     */
    run() {
        this.io = readline.createInterface(process.stdin, process.stdout);
        this.io.on('line', this.handleLine.bind(this));
        this.io.on('close', this.handleIOClose.bind(this));
    }

    /**
     * This function is called each time the bot receives input. It converts
     * the raw input to an Array of Strings and calls either the `action`,
     * `settings` or `update` function depending on the first item in the list.
     *
     * See the "Communicating with the game engine" section on the "Getting started" page
     * for full details on the IO between the engine and the bot.
     *
     * @param {String} data
     */
    handleLine(data) {
        // stop if line doesn't contain anything
        if (data.length === 0) {
            return;
        }

        const lines = data.trim().split('\n');

        while (0 < lines.length) {

            const line = lines.shift().trim();
            const lineParts = line.split(" ");

            // stop if lineParts doesn't contain anything
            if (lineParts.length === 0) {
                return;
            }

            // get the input command and convert to camel case
            const command = utils.toCamelCase(lineParts.shift());

            // invoke command if function exists and pass the data along
            // then return response if exists
            if (this[command] instanceof Function) {

                const response = this[command](lineParts);

                if (response && 0 < response.length) {
                    process.stdout.write(response + '\n');
                }
            } else {
                process.stderr.write('Unable to execute command: ' + command + ', with data: ' + lineParts + '\n');
            }
        }
    }

    handleIOClose() {
        process.exit(0);
    }

    /**
     * Writes a setting to the Bot.gameSettings object
     * @param {Array} data
     */
    settings(data) {
        const key = data[0];
        const value = data[1];

        // set key to value
        this.gameSettings[key] = value;
    }

    /**
     * Called when the engine sends an `update` message.
     * This function either updates the game data (field or round) or
     * the player data.
     *
     * @param {Array} data
     */
    update(data) {
        const command = data.shift();

        if (command === 'game') {
            this.updateGame(data);
        }

        this.updatePlayerData(data);
    }

    /**
     * Updates the game state with data provided by the engine
     *
     * @param {Array} data
     */
    updateGame(data) {

        if (data[0] === 'round') {
            this.state.round = parseInt(data[1], 10);
        }
        else if (data[0] === 'field') {
            this.state.field = data[1].split(',');
        }
    }

    /**
     * Updates the game state with data provided by the engine
     *
     * @param {Array} data
     */
    updatePlayerData(data) {
        const playerId = data[0];

        if(data[1] === 'snippets') {
            this.state.players[playerId].snippets = parseInt(data[2], 10);
        }
        else if (data[1] === 'has_weapon') {
            this.state.players[playerId].hasWeapon = (data[2] === 'true');
        }
        else if (data[1] === 'is_paralyzed') {
            this.state.players[playerId].isParalyzed = (data[2] === 'true');
        }
    }

    /**
     * This function is executed every time the game engine requests the bot
     * to make a move. It executes the strategy defined in the constructor and
     * returns the resulting move, which is sent to the engine by the Bot.run method.
     *
     * @param {Array} data
     * @returns {String | null}
     */
    action(data) {
        if (data[0] === 'move') {
            this.state.timebank = parseInt(data[1], 10);
            return this.strategy.execute(this.gameSettings, this.state);
        }
    }
}

module.exports = Bot;
