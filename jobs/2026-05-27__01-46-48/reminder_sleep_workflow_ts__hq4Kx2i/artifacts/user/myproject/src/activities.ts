import * as fs from 'fs';
import * as path from 'path';

const LOG_FILE = '/workspace/reminder.log';

/**
 * Notify activity: appends "Notified: <message>" to the log file and returns the string.
 */
export async function Notify(message: string): Promise<string> {
  const line = `Notified: ${message}`;

  // Ensure parent directory exists
  const dir = path.dirname(LOG_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.appendFileSync(LOG_FILE, line + '\n', 'utf8');

  return line;
}
