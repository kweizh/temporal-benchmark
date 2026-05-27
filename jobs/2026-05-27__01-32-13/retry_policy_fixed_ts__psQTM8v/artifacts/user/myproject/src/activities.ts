import * as fs from 'fs';
import { Context } from '@temporalio/activity';
import { ApplicationFailure } from '@temporalio/common';

const ATTEMPTS_LOG_PATH = '/workspace/attempts.log';

export async function flakyTask(): Promise<void> {
  const attempt = Context.current().info.attempt;
  fs.appendFileSync(ATTEMPTS_LOG_PATH, `attempt=${attempt}\n`);

  throw ApplicationFailure.create({
    message: 'flaky task failed',
    type: 'FlakyTaskError',
  });
}
