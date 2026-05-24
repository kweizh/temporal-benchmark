import { Context, ApplicationFailure } from '@temporalio/activity';
import * as fs from 'fs';

export async function flakyTask(): Promise<void> {
  const attempt = Context.current().info.attempt;
  const logLine = `Attempt ${attempt}\n`;
  fs.appendFileSync('/workspace/attempts.log', logLine);

  throw ApplicationFailure.create({
    message: 'Deliberate failure',
    nonRetryable: false,
  });
}
