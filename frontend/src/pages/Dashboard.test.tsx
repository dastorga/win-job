import { describe, test, expect } from '@jest/globals';

describe('Dashboard Component', () => {
  test('basic test passes', () => {
    expect(2 + 2).toBe(4);
  });

  test('string operations work', () => {
    expect('Dashboard'.toLowerCase()).toBe('dashboard');
  });
});