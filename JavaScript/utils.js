/**
 * This file is part of the Booking.com Hack-man JavaScript starter bot
 *
 * Last update: September 29, 2016
 *
 * @author Niko van Meurs <niko@riddles.io>
 * @License MIT License (http://opensource.org/Licenses/MIT)
 */

function toCamelCase(string) {

    return string.replace('/', '_').replace(/_[a-z]/g, function (match) {
        return match.toUpperCase().replace('_', '');
    });
}

module.exports = {
    toCamelCase
};
