import { describe, test, expect } from '@jest/globals';

describe('App Component', () => {
  test('basic test passes', () => {
    expect(1 + 1).toBe(2);
  });

  test('React module exists', () => {
    expect(typeof require('react')).toBe('object');
  });
});