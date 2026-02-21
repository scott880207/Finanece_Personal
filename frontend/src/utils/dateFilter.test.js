import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { filterDataByTimeRange } from './dateFilter';

describe('filterDataByTimeRange', () => {
    beforeEach(() => {
        // Mock system time to 2026-02-22
        vi.useFakeTimers();
        vi.setSystemTime(new Date(2026, 1, 22)); // Feb 22, 2026
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    const mockData = [
        { date: '2025-01-01', value: 100 }, // Over 1 year ago
        { date: '2025-02-21', value: 110 }, // More than 1 year ago (since cutoff is 2025-02-22)
        { date: '2025-02-22', value: 120 }, // Exactly 1 year ago
        { date: '2025-05-15', value: 130 }, // Within 1 year, outside 3M
        { date: '2025-11-20', value: 140 }, // Outside 3M (3 months ago is 2025-11-22)
        { date: '2025-11-22', value: 150 }, // Exactly 3 months ago
        { date: '2026-01-10', value: 160 }, // Within 3 months
        { date: '2026-02-22', value: 170 }, // Today
    ];

    it('returns all data when range is ALL', () => {
        const result = filterDataByTimeRange(mockData, 'ALL');
        expect(result.length).toBe(8);
    });

    it('filters data within the last 1 year', () => {
        const result = filterDataByTimeRange(mockData, '1Y');
        expect(result.length).toBe(6);
        expect(result[0].date).toBe('2025-02-22');
        expect(result[result.length - 1].date).toBe('2026-02-22');
    });

    it('filters data within the last 3 months', () => {
        const result = filterDataByTimeRange(mockData, '3M');
        expect(result.length).toBe(3);
        expect(result[0].date).toBe('2025-11-22');
        expect(result[result.length - 1].date).toBe('2026-02-22');
    });

    it('handles empty or invalid inputs gracefully', () => {
        expect(filterDataByTimeRange(null, '3M')).toEqual([]);
        expect(filterDataByTimeRange(undefined, '1Y')).toEqual([]);
        expect(filterDataByTimeRange({}, 'ALL')).toEqual([]);
    });
});
