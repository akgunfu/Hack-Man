/**
 * This file is part of the Booking.com Hack-man JavaScript starter bot
 *
 * Last update: September 29, 2016
 *
 * @author Niko van Meurs <niko@riddles.io>
 * @License MIT License (http://opensource.org/Licenses/MIT)
 */

/**
 * Checks whether the coordinate is within the game field dimensions
 *
 * @param settings
 * @param coordinate
 * @returns {boolean}
 */
function isInBounds(settings, coordinate) {

    if (0 >= coordinate.x || coordinate.x >= settings.field_width) {
        return false;
    }

    if (0 >= coordinate.y || coordinate.y >= settings.field_height) {
        return false;
    }

    return true;
}

/**
 * Returns a list of all valid moves, including pass
 *
 * @param {Object} gameSettings The bot's game settings
 * @param {Object} state        The game state for which to calculate the available moves
 * @returns {Array}             List of available moves
 */
function getAvailableMoves(gameSettings, state) {

    const myPosition = getCoordinateFor(gameSettings, state.field, gameSettings.your_botid);
    const neighboringFields = getNeighboringFields(gameSettings, state.field, myPosition);
    const availableMoves = ['pass'];

    Object.keys(neighboringFields).forEach(function (key) {

        if (neighboringFields[key] !== 'x') {
            availableMoves.push(key);
        }
    });

    return availableMoves;
}

/**
 * Returns the field size
 * @param {Object} settings
 * @returns {Number}
 */
function getFieldSize(settings) {
    const fieldWidth = parseInt(settings.field_width, 10);
    const fieldHeight = parseInt(settings.field_height, 10);

    return fieldWidth * fieldHeight;
}

/**
 * Returns the coordinate at which the bot with id botId is located
 *
 * @param {Object} settings The bot's settings object
 * @param {Array}  field    The field object
 * @param {String} botId    The id of the bot for which to determine its position
 * @returns {{x, y}|{x: Number, y: Number}|null}
 */
function getCoordinateFor(settings, field, botId) {
    const index = field.findIndex(f => f === botId);
    return indexToCoordinate(settings, index);
}

/**
 * Returns the neighboring fields for a given coordinate
 *
 * @param {Object} settings The bot's settings object
 * @param {Array}  field    The field object
 * @param {{ x:Number, y:Number }} coordinate The coordinate for which to return the neighboring fields
 * @returns {Object}
 */
function getNeighboringFields(settings, field, coordinate) {

    let neighboringFields = {};

    const up = { x: coordinate.x, y: coordinate.y - 1 };
    const down = { x: coordinate.x, y: coordinate.y + 1 };
    const left = { x: coordinate.x - 1, y: coordinate.y };
    const right = { x: coordinate.x + 1, y: coordinate.y };

    process.stderr.write('up: ' + JSON.stringify(up) + '\n');
    process.stderr.write('down: ' + JSON.stringify(down) + '\n');
    process.stderr.write('left: ' + JSON.stringify(left) + '\n');
    process.stderr.write('right: ' + JSON.stringify(right) + '\n');

    if (isInBounds(settings, up)) {
        const upIndex = coordinateToIndex(settings, up);
        neighboringFields.up = field[upIndex];
    }

    if (isInBounds(settings, down)) {
        const downIndex = coordinateToIndex(settings, down);
        neighboringFields.down = field[downIndex];
    }

    if (isInBounds(settings, left)) {
        const leftIndex = coordinateToIndex(settings, left);
        neighboringFields.left = field[leftIndex];
    }

    if (isInBounds(settings, right)) {
        const rightIndex = coordinateToIndex(settings, right);
        neighboringFields.right = field[rightIndex];
    }

    return neighboringFields;
}

/**
 * Returns a coordinate for the given state.fields array index
 *
 * @param {Object} settings The bot's settings object
 * @param {Number} index
 * @returns {{ x:Number, y:Number } | null}
 */
function indexToCoordinate(settings, index) {
    if (index >= getFieldSize(settings)) {
        process.stderr.write('index > fieldsize\n')
        return null;
    }

    const fieldWidth = parseInt(settings.field_width, 10);

    const x = index % fieldWidth;
    const y = Math.floor(index / fieldWidth);

    return { x: x, y: y };
}

/**
 * Returns the index for the fields array for the given coordinate
 *
 * @param {Object}                 settings   The bot's settings object
 * @param {{ x:Number, y:Number }} coordinate
 * @returns {Number}
 */
function coordinateToIndex(settings, coordinate) {

    if (!isInBounds(settings, coordinate)) {
        return -1;
    }

    const fieldWidth = settings.field_width;

    return coordinate.y * fieldWidth + coordinate.x;
}

module.exports = {
    isInBounds,
    getAvailableMoves,
    getCoordinateFor,
    getFieldSize,
    getNeighboringFields,
    indexToCoordinate,
    coordinateToIndex
};
