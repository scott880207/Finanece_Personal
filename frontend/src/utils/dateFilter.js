/**
 * Filters a list of data entries based on a specific time range.
 * @param {Array} data - Array of objects, each must have a 'date' property (string or Date).
 * @param {string} range - '3M', '1Y', or 'ALL'
 * @returns {Array} Filtered list
 */
export const filterDataByTimeRange = (data, range) => {
    if (!data || !Array.isArray(data)) return [];
    if (range === 'ALL') return data;

    const today = new Date();
    // We want to calculate the cutoff date based on today
    let cutoff = new Date(today);

    if (range === '3M') {
        cutoff.setMonth(today.getMonth() - 3);
    } else if (range === '1Y') {
        cutoff.setFullYear(today.getFullYear() - 1);
    }

    // Reset time part to start of day for accurate Date comparison
    cutoff.setHours(0, 0, 0, 0);

    return data.filter(entry => {
        const entryDate = new Date(entry.date);
        return entryDate >= cutoff;
    });
};
