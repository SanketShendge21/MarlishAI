import { MAX_INPUT_LENGTH, MIN_INPUT_LENGTH } from './constants';

export function sanitizeInput(text) {
  if (!text) return '';
  return text
    .replace(/<[^>]*>/g, '')        // Strip HTML tags
    .replace(/[<>"'`]/g, '')        // Remove dangerous chars
    .slice(0, MAX_INPUT_LENGTH)     // Enforce max length
    .trim();
}

export function isValidInput(text) {
  if (!text || text.trim().length < MIN_INPUT_LENGTH) return false;
  if (text.length > MAX_INPUT_LENGTH) return false;
  return true;
}
