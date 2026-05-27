import * as fs from 'fs';
import * as path from 'path';

export async function Notify(message: string): Promise<string> {
  const logDir = '/workspace';
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  const logFile = path.join(logDir, 'reminder.log');
  const logMessage = `Notified: ${message}`;
  fs.appendFileSync(logFile, logMessage + '\n');
  return logMessage;
}
