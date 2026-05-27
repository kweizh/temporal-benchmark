import * as fs from 'fs';
import { Context, ApplicationFailure } from '@temporalio/activity';

export async function flakyTask(): Promise<void> {
  const attempt = Context.current().info.attempt;
  fs.appendFileSync('/workspace/attempts.log', `Attempt ${attempt} failed\n`);
  throw ApplicationFailure.create({
    message: `flakyTask failed on attempt ${attempt}`,
  });
}
